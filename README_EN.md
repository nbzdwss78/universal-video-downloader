# 📦 Installation Guide

## 1. Dependencies

Before using this tool, make sure the following components are installed on your system:

### 🐍 **conda**
Recommended: Anaconda or Miniconda  
Used for managing Python virtual environments.

### 🟩 **Node.js**
Required as the local JavaScript execution environment (used by parts of the Chrome extension integration).

### 🎬 **FFmpeg**
Responsible for video/audio merging, transcoding, and audio extraction.

**Linux Installation Example:**

```bash
sudo apt install ffmpeg
```

### 📥 **yt-dlp**
The core engine used to parse and download videos, audio, and subtitles from various websites.

Install with:

```bash
pip install yt-dlp
```

---

## 2. Install the Chrome Extension

1. Open the Chrome browser  
2. Navigate to: `chrome://extensions`  
3. Enable **Developer Mode** in the top-right corner  
4. Click **“Load unpacked”**  
5. Select the **`chrome-extension/`** folder from this project  

Once loaded, the extension will automatically capture video/audio requests from webpages.

---

## 3. Install Python Dependencies

Create and activate your Python environment (conda recommended):

```bash
conda create -n uvd python=3.9
conda activate uvd
```

Install all required third-party libraries:

```bash
pip install -r requirements.txt
```

---

## 4. Start the Multi-Platform Download Server

Run the core service:

```bash
python server-muavcookie.py
```

This server provides:

- Video and audio downloading  
- Cookie management  
- Multi-platform support (YouTube, X/Twitter, Bilibili, Netease Cloud Music, etc.)  
- Task scheduling and status tracking  

Once started, the server listens for incoming download requests from the Chrome extension.

---

## 5. How to Use

1. Open any webpage containing video or audio  
2. Click the **Universal Video Downloader** extension icon in Chrome  
3. First click **“Refresh Cookie”**  
   - Ensures login cookies are synced  
   - Prevents parsing failures due to authentication  
4. Select **“Download Audio”** or **“Download Video”**  
5. A new confirmation page will open  
   - Review the detected media information  
   - Click **Download** to start the process  

Downloaded files will be saved by default to:

```
./download/
```

---

# ⚠️ Important Notice

### 1️⃣ For learning and personal research only  
This software is intended **only for educational and personal use**.  
Commercial use is strictly prohibited.  
The developer bears **no responsibility** for any account bans, restrictions, or legal issues caused by misuse.

### 2️⃣ Not recommended for complete beginners  
This tool is designed for users with **basic development knowledge**.  
If you are a beginner and need assistance, limited paid technical support is available.

---
