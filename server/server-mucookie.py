from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import threading
import uuid
import os
import shutil

# =================================================================
# 初始化
# =================================================================
app = Flask(__name__)
EXT_ORIGIN = "chrome-extension://cmmeiigobejkpakmfbnmopgcbohgdaol"

CORS(app, resources={r"/*": {"origins": EXT_ORIGIN}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = EXT_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

tasks = {}

# =================================================================
# 1. 接收 Cookie
# =================================================================
@app.post("/update_cookie")
def update_cookie():
    data = request.get_json()
    cookies = data.get("cookies")

    if not cookies or not isinstance(cookies, str):
        return {"status": "error", "message": "Cookie 内容为空或格式无效"}, 400

    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookies)

    return {"status": "ok", "message": "Cookie 已更新成功"}

# =================================================================
# 2. URL 平台识别器（核心）
# =================================================================
def detect_platform(url: str):
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "bilibili.com" in url:
        return "bilibili"
    if "douyin.com" in url:
        return "douyin"
    if "tiktok.com" in url:
        return "tiktok"
    if "instagram.com" in url:
        return "instagram"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if "facebook.com" in url:
        return "facebook"

    # 默认平台（yt-dlp 支持的任何平台）
    return "generic"

# =================================================================
# 3. 平台参数生成器（多平台适配）
# =================================================================
def build_ydl_opts(platform, url, task_id, node_path):
    opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/{platform}/%(title)s-%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "progress_hooks": [lambda d: progress_hook(task_id, d)],
        "cookiefile": COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        "ignoreerrors": False,
		"writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "srt",
        "subtitleslangs": ["auto", "zh-Hans"],
    }

    # ----------------------
    # YouTube（最复杂）
    # ----------------------
    if platform == "youtube":
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "exec": node_path,                      # 必须，有 nsig 解密
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web_safari"]  # 最稳定组合
                }
            }
        })

    # ----------------------
    # Bilibili
    # ----------------------
    elif platform == "bilibili":
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "user_agent": "Mozilla/5.0",
            "http_headers": {
                "Referer": "https://www.bilibili.com"
            }
        })

    # ----------------------
    # Douyin / TikTok 抖音系
    # ----------------------
    elif platform in ["douyin", "tiktok"]:
        opts.update({
            "format": "mp4",
            "extractor_args": {
                "douyin": {"fix_srt": True},
                "tiktok": {"fix_srt": True},
            }
        })

    # ----------------------
    # Instagram Reels / Story
    # ----------------------
    elif platform == "instagram":
        opts.update({
            "format": "best",
            "user_agent": "Mozilla/5.0"
        })

    # ----------------------
    # Twitter (X)
    # ----------------------
    elif platform == "twitter":
        opts.update({
            "format": "best",
            "user_agent": "Mozilla/5.0"
        })

    # ----------------------
    # Facebook
    # ----------------------
    elif platform == "facebook":
        opts.update({
            "format": "best",
            "user_agent": "Mozilla/5.0"
        })

    return opts

# =================================================================
# 4. 下载进度回调
# =================================================================
def progress_hook(task_id, d):
    if d["status"] == "downloading":
        tasks[task_id]["progress"] = d.get("_percent_str", "0%")

# =================================================================
# 5. 下载线程（所有平台共享）
# =================================================================
def download_worker(task_id, url):
    platform = detect_platform(url)
    tasks[task_id]["status"] = f"downloading-{platform}"

    # 自动检测 Node.js，用于 YouTube 解密
    node_path = shutil.which("node") or shutil.which("node.exe")

    # 构建平台配置
    ydl_opts = build_ydl_opts(platform, url, task_id, node_path)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        tasks[task_id]["status"] = "finished"

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

# =================================================================
# 6. 创建任务
# =================================================================
@app.post("/task/create")
def create_task():
    req = request.get_json()
    url = req["url"]

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "url": url,
        "platform": detect_platform(url),
        "status": "queued",
        "progress": "0%"
    }

    # 开启新线程处理下载任务
    threading.Thread(target=download_worker, args=(task_id, url), daemon=True).start()
    return jsonify(tasks[task_id])

# =================================================================
# 7. 查询任务（前端轮询）
# =================================================================
@app.get("/task/<task_id>")
def get_task(task_id):
    return jsonify(tasks.get(task_id, {"error": "task not found"}))

# =================================================================
# 启动服务
# =================================================================
app.run(port=18888)
