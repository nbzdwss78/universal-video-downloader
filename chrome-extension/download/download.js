console.log("download.js loaded");
let receivedUrl = null;
let currentMode = "video";
let currentTaskId = null;

// 接收 popup 发来的 URL
chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === "setVideoUrl") {
        receivedUrl = msg.url;
		currentMode = msg.mode || "video";

    //document.getElementById("videoUrl").innerText = currentUrl;
    document.getElementById("mode").innerText = currentMode;
    document.getElementById("videoUrl").innerText = receivedUrl;
    }
});

// 点击下载
document.getElementById("downloadBtn").onclick = async () => {
    if (!receivedUrl) {
        alert("未收到视频地址！");
        return;
    }

    const resp = await fetch("http://127.0.0.1:18888/task/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: receivedUrl,mode: currentMode })
    });
if (!resp.ok) {
    alert("后端异常：" + resp.status);
    return;
}
    const data = await resp.json();
    currentTaskId = data.task_id;

    pollTask();
};

// 轮询任务状态
async function pollTask() {
    if (!currentTaskId) return;

    const infoBox = document.getElementById("taskInfo");

    const timer = setInterval(async () => {
        const resp = await fetch(`http://127.0.0.1:18888/task/${currentTaskId}`);
        const data = await resp.json();

        infoBox.textContent = JSON.stringify(data, null, 2);

        if (data.status === "finished" || data.status === "error") {
            clearInterval(timer);
        }
    }, 800);
}
