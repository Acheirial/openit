# Agent rules

代码内容保持**简单、准确、实用**，避免冗余注释。

禁止在本地进行抓取。不要对本机发起节点测活、端口扫描、DNS 扫节点或对订阅节点做连通性探测。订阅采集与测活只在远程 CI 或用户明确要求的环境执行。

Clash 系产物按 Mihomo Meta/Alpha 生成。`target=clash` 走 Mihomo 解析桥。公开文件名 `Clash.yaml` 只为兼容旧订阅 URL。
