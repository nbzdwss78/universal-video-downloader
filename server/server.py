from flask import Flask, request, jsonify
import yt_dlp
import threading
import uuid
import os
import shutil

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "www.youtube.com_cookies.txt")

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

tasks = {}

def check_cookie_valid():
    if not os.path.exists(COOKIE_FILE):
        return False
    if os.path.getsize(COOKIE_FILE) < 200:
        return False

    content = open(COOKIE_FILE, "r", encoding="utf-8").read()
    return ("SAPISID" in content) or ("APISID" in content)

def download_worker(task_id, url):
    tasks[task_id]["status"] = "downloading"
    tasks[task_id]["progress"] = "0%"

    cookie_valid = check_cookie_valid()

    # 自动寻找 node 路径
    node_path = shutil.which("node") or shutil.which("node.exe")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",

        # ★★ 强制启用 JS Runtime（防止 nsig / challenge 失败）
        "exec": node_path,

        # ★★ 强制指定 YouTube Client（避免 SABR 丢格式）
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web_safari"]
            }
        },

        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s-%(id)s.%(ext)s",
        "progress_hooks": [lambda d: progress_hook(task_id, d)],
    }

    # 使用 cookie 文件（必须：否则仍然会出现 Sign in 错误）
    if cookie_valid:
        ydl_opts["cookiefile"] = COOKIE_FILE
    else:
        tasks[task_id]["cookie_warning"] = "Cookie 文件无效，请重新导出 www.youtube.com_cookies.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        tasks[task_id]["status"] = "finished"
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

def progress_hook(task_id, d):
    if d["status"] == "downloading":
        tasks[task_id]["progress"] = d.get("_percent_str", "0%")

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

@app.get("/task/<task_id>")
def get_task(task_id):
    return jsonify(tasks.get(task_id, {"error": "task not found"}))

app.run(port=18888)
