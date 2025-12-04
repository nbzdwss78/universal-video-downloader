// 加载 cookie.js（运行在扩展后台，而不是网页）
importScripts("cookie/cookie.js");


// 打开下载器页面 + 传 URL
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "openDownloader") {
        chrome.tabs.create({
            url: chrome.runtime.getURL("download/download.html")
        }, (newTab) => {
            setTimeout(() => {
                chrome.tabs.sendMessage(newTab.id, {
                    type: "setVideoUrl",
                    url: msg.url,
					mode: msg.mode
                });
            }, 600);
        });
    }
});


// 刷新 Cookie（最关键部分）
chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
    if (msg.type === "refresh_cookie") {

        try {
            // 直接在扩展后台环境执行（chrome.cookies 可访问）
            const cookieText = await exportYoutubeCookies();

            // 发给 Python 服务
            await fetch("http://127.0.0.1:18888/update_cookie", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cookies: cookieText }),
            });

            sendResponse({ ok: true });

        } catch (e) {
            sendResponse({ ok: false, error: e.toString() });
        }
    }

    return true;
});
