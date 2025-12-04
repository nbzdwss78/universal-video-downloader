function toNetscapeCookie(c) {
    // 修复 domain：必须以 "." 开头
    let domain = c.domain.startsWith(".") ? c.domain : "." + c.domain;

    // Netscape 格式：
    // domain    HttpOnly    path    secure    expiration    name    value
    return `${domain}\tTRUE\t${c.path}\t${c.secure ? "TRUE" : "FALSE"}\t${Math.floor(c.expirationDate || 0)}\t${c.name}\t${c.value}`;
}

async function exportYoutubeCookies() {
    const cookies = await chrome.cookies.getAll({ domain: ".youtube.com" });

    let netscape = "# Netscape HTTP Cookie File\n";

    for (const c of cookies) {
        netscape += toNetscapeCookie(c) + "\n";
    }

    return netscape;
}
