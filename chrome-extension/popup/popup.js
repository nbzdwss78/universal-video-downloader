document.getElementById("downloadVideo").onclick = () => startDownload("video");
document.getElementById("downloadAudio").onclick = () => startDownload("audio");

function startDownload(mode) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs[0].url;

    chrome.runtime.sendMessage({
      type: "openDownloader",
      url,
      mode
    });
  });
}
chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
  if (msg.type === "refresh_cookie") {

    try {
      await chrome.scripting.executeScript({
        target: { tabId: sender.tab.id },
        files: ["cookie/cookie.js"]
      });

      await sendCookieToServer();
      sendResponse({ ok: true });
    } catch (e) {
      sendResponse({ ok: false, error: e.toString() });
    }
  }
  return true;
});
document.getElementById("refreshCookie").onclick = () => {
  chrome.runtime.sendMessage({ type: "refresh_cookie" }, (resp) => {
    if (resp.ok) alert("Cookie 已刷新！");
    else alert("刷新失败：" + resp.error);
  });
};
