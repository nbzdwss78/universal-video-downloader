from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import threading
import uuid
import os
import shutil

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

# ===============================================
# 1. 更新 Cookie（从浏览器传来）
# ===============================================
@app.post("/update_cookie")
def update_cookie():
    data = request.get_json()
    cookies = data.get("cookies", "")

    if not cookies:
        return {"status": "error", "message": "cookie 为空"}, 400

    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookies)

    return {"status": "ok", "message": "cookie 已更新"}


# ===============================================
# 2. URL 平台识别器
# ===============================================
def detect_platform(url: str):
    u = url.lower()
    if "youtube" in u or "youtu.be" in u: return "youtube"
    if "bilibili" in u: return "bilibili"
    if "douyin" in u: return "douyin"
    if "tiktok" in u: return "tiktok"
    if "instagram" in u: return "instagram"
    if "twitter" in u or "x.com" in u: return "twitter"
    return "generic"


# ===============================================
# 3. 视频下载参数
# ===============================================
def build_video_opts(platform, task_id, node_path):

    opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/{platform}/%(title)s-%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "progress_hooks": [lambda d: progress_hook(task_id, d)],
        "cookiefile": COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "srt",
        "subtitleslangs": ["auto", "zh-Hans"],
        "retries": 20,
        "extractor_retries": 10,
    }

    # YouTube 需要 nsig 解密
    if platform == "youtube":
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "exec": node_path,
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "android", "web_safari"]
                }
            }
        })

    elif platform == "bilibili":
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "http_headers": {"Referer": "https://www.bilibili.com"}
        })

    elif platform in ["douyin", "tiktok"]:
        opts.update({
            "format": "mp4",
        })

    else:
        opts.update({"format": "best"})

    return opts


# ===============================================
# 4. 音频下载参数（转换为 MP3）
# ===============================================
def build_audio_opts(task_id):
    audio_dir = os.path.join(DOWNLOAD_DIR, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    return {
        "format": "bestaudio/best",
        "outtmpl": f"{audio_dir}/%(title)s-%(id)s.%(ext)s",
        "progress_hooks": [lambda d: progress_hook(task_id, d)],
        "cookiefile": COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320"
        }],
        "retries": 20,
        "extractor_retries": 10,
    }


# ===============================================
# 5. 进度回调
# ===============================================
def progress_hook(task_id, d):
    if d["status"] == "downloading":
        tasks[task_id]["progress"] = d.get("_percent_str", "0%")


# ===============================================
# 6. 下载线程
# ===============================================
def download_worker(task_id, url, mode):
    platform = detect_platform(url)
    tasks[task_id]["status"] = f"downloading-{mode}"

    node_path = shutil.which("node") or shutil.which("node.exe")

    if mode == "audio":
        ydl_opts = build_audio_opts(task_id)
    else:
        ydl_opts = build_video_opts(platform, task_id, node_path)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        tasks[task_id]["status"] = "finished"

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)


# ===============================================
# 7. 创建任务
# ===============================================
@app.post("/task/create")
def create_task():
    req = request.get_json()
    url = req["url"]
    mode = req.get("mode", "video")  # video 或 audio

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "url": url,
        "mode": mode,
        "platform": detect_platform(url),
        "status": "queued",
        "progress": "0%"
    }

    threading.Thread(target=download_worker, args=(task_id, url, mode), daemon=True).start()

    return jsonify(tasks[task_id])


# ===============================================
# 8. 查询任务
# ===============================================
@app.get("/task/<task_id>")
def get_task(task_id):
    return jsonify(tasks.get(task_id, {"error": "task not found"}))


# ===============================================
# 入口
# ===============================================
app.run(port=18888)
