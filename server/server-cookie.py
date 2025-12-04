from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import threading
import uuid
import os
import shutil

# -------------------------------------------------------------------
# 初始化
# -------------------------------------------------------------------
app = Flask(__name__)

# 允许 Chrome 扩展访问（解决 CORS）
CORS(app, supports_credentials=True)

EXT_ORIGIN = "chrome-extension://cmmeiigobejkpakmfbnmopgcbohgdaol"

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = EXT_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "www.youtube.com_cookies.txt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 存储任务列表
tasks = {}

# -------------------------------------------------------------------
# Cookie 更新（插件自动发送）
# -------------------------------------------------------------------
@app.post("/update_cookie")
def update_cookie():
    """接收 Chrome 插件发来的 Cookie，并保存为 yt-dlp 可用格式"""
    data = request.get_json()
    cookies = data.get("cookies", "")

    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookies)

    return {"status": "ok", "message": "Cookie 已更新成功 ✓"}

# -------------------------------------------------------------------
# 任务下载线程
# -------------------------------------------------------------------
def progress_hook(task_id, d):
    if d["status"] == "downloading":
        tasks[task_id]["progress"] = d.get("_percent_str", "0%")

def download_worker(task_id, url):
    tasks[task_id]["status"] = "downloading"
    tasks[task_id]["progress"] = "0%"

    # 自动检测 node（用于 YouTube n-sig 解密）
    node_path = shutil.which("node") or shutil.which("node.exe")

    # yt-dlp 配置（YouTube 2024–2025 最新加密兼容）
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",

        # Node.js 支持（解析 nsig / challenge 必须）
        "exec": node_path,

        # 强制使用 Android / Safari 客户端避免 SABR 限制
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web_safari"]
            }
        },

        # 你插件上传的 cookie
        "cookiefile": COOKIE_FILE,

        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s-%(id)s.%(ext)s",
        "progress_hooks": [lambda d: progress_hook(task_id, d)],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        tasks[task_id]["status"] = "finished"

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

# -------------------------------------------------------------------
# 创建任务
# -------------------------------------------------------------------
@app.post("/task/create")
def create_task():
    req = request.get_json()
    url = req["url"]

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "url": url,
        "status": "queued",
        "progress": "0%"
    }

    threading.Thread(target=download_worker, args=(task_id, url), daemon=True).start()
    return jsonify(tasks[task_id])

# -------------------------------------------------------------------
# 查询任务
# -------------------------------------------------------------------
@app.get("/task/<task_id>")
def get_task(task_id):
    return jsonify(tasks.get(task_id, {"error": "task not found"}))

# -------------------------------------------------------------------
# 启动服务
# -------------------------------------------------------------------
app.run(port=18888)
