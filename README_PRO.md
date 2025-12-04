# Universal Video Downloader  
*A Cross-Platform Video & Audio Downloader Powered by Chrome Extension + Local Server*

<p align="left">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg">
  <img src="https://img.shields.io/badge/python-3.9%2B-brightgreen">
  <img src="https://img.shields.io/badge/node.js-18%2B-green">
  <img src="https://img.shields.io/badge/yt--dlp-latest-orange">
  <img src="https://img.shields.io/badge/license-MIT-yellow">
</p>

---

# 📑 Table of Contents
- [✨ Features](#-features)
- [📦 Dependencies](#-dependencies)
- [🧩 Project Structure](#-project-structure)
- [🛠 Installation Guide](#-installation-guide)
- [🚀 Usage Guide](#-usage-guide)
- [🏗 Architecture](#-architecture)
- [🔁 Download Flow](#-download-flow)
- [⚠ Important Notice](#-important-notice)
- [📄 License](#-license)

---

# ✨ Features

- 🧩 **Chrome Extension Media Sniffer**  
  Automatically captures video/audio streams from webpages.

- 🎬 **Multi-Platform Download Engine**  
  Works with YouTube, X/Twitter, Bilibili, Netease Cloud Music and more.

- 🔐 **Cookie Syncing**  
  Supports sites requiring login.

- ⬇️ **High-Quality Video/Audio Download**  
  Uses `yt-dlp` + `ffmpeg` for best format handling.

- 📁 **Task Management**  
  Multiple downloads with progress tracking.

- ⚙️ **Extensible Design**  
  Easy to integrate new platforms.

---

# 📦 Dependencies

- conda (Anaconda / Miniconda)
- Node.js 18+
- Python 3.9+
- FFmpeg
- yt-dlp

---

# 🧩 Project Structure

```
universal-video-downloader/
├── chrome-extension/
├── server/
│   ├── server-muavcookie.py
│   ├── downloader/
│   ├── cookies/
│   ├── tasks/
│   └── downloads/
└── README.md
```

---

# 🛠 Installation Guide

## 1. Python Env

```bash
conda create -n uvd python=3.9
conda activate uvd
pip install -r requirements.txt
```

## 2. Chrome Extension

- Open Chrome → chrome://extensions  
- Enable Developer Mode  
- Load unpacked → select `chrome-extension/`

## 3. Start Server

```bash
python server-muavcookie.py
```

---

# 🚀 Usage Guide

1. Open a webpage with media.
2. Click extension icon.
3. Refresh Cookie.
4. Choose Download Audio or Video.
5. Confirm and download.

Saved to:

```
./download/
```

---

# 🏗 Architecture

```mermaid
flowchart TD
    A[Chrome Extension] -->|URL + Cookies| B[Local Python Server]
    B --> C[yt-dlp Engine]
    C --> D[FFmpeg Processor]
    D --> E[Download Output ./download/]
    B --> F[Task Manager API]
    F --> A
```

---

# 🔁 Download Flow

```mermaid
sequenceDiagram
    participant User
    participant Extension
    participant Server
    participant YTDLP as yt-dlp/FFmpeg

    User->>Extension: Click Download
    Extension->>Extension: Capture Media URL
    Extension->>Server: POST /task
    Server->>YTDLP: Parse & Download
    YTDLP-->>Server: Progress
    Server-->>Extension: Status Update
    Extension-->>User: Download Complete
```

---

# ⚠ Important Notice

- For personal learning only.
- Commercial use prohibited.
- Developer not responsible for account bans or legal issues.
- Limited paid support for non-technical users.

---

# 📄 License

MIT License © 2025
