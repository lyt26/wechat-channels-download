# 微信视频号下载 — 原理与踩坑

## 为什么网页打不开视频

短链 `https://weixin.qq.com/sph/{id}` 会 302 到：

```
https://channels.weixin.qq.com/finder-preview/pages/sph?id={id}
```

该预览页会请求：

```
POST /finder-preview/api/feed/get_feed_info
```

返回里常见字段只有：

- `authorInfo`（昵称、头像）
- `feedInfo.description` / 点赞转发等
- `feedInfo.coverUrl`（封面图 CDN）
- `sceneInfo.dynamicExportId`（形如 `export/UzFf...`）

**没有** `videoUrl`。UI 提示扫码进微信观看。因此只靠预览页 DOM / `get_feed_info` 无法下视频。

`dynamicExportId` 可作辅助标识，但平台管理端页面多需登录「视频号助手」，不适合无登录自动化。

## 解析服务如何补齐 videoUrl

在线解析页 https://sph.litao.workers.dev/ 调用：

```
POST /api/fetch_video_profile
{"url":"<分享链>"}
```

成功时 `feedInfo` 会带：

- `videoUrl` / `h264VideoInfo.videoUrl` / `h265VideoInfo.videoUrl`
- 仍可能带 `coverUrl`、互动计数、`description`

该服务与开源项目 [ltaoo/wx_channels_download](https://github.com/ltaoo/wx_channels_download) 同源文档；本质是把分享链解析成微信侧可用的媒体元数据。**第三方服务可能变更或不可用**，Skill 主路径失败时改用 PC 微信插件方案。

## CDN 下载注意

- 主机：`finder.video.qq.com`（路径含 `stodownload`、`encfilekey`、`token`、`sign`）
- Query 参数有时效；拿到后尽快下载，不要当永久直链存档
- 建议 `Referer: https://channels.weixin.qq.com/`
- H.264 兼容性通常优于 H.265；默认优先 `videoUrl` 或 `h264VideoInfo`

## 与其它方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| sph 解析 API + curl | 无微信客户端、可脚本化 | 依赖第三方；链过期要重解析 |
| yt-dlp | 其它站点通用 | **当前不支持视频号** |
| finder-preview 自抓 | 官方页 | 通常只有封面 |
| wx_channels_download + PC 微信 | 官方播放链路、质量可选 | 需管理员、证书、本机微信 |
| 商业 API（TikHub / JustOne 等） | 结构化 objectId | 要 Key、付费 |

## 一次真实样例（流程验证）

输入：`https://weixin.qq.com/sph/AS44aBHSMu`

1. yt-dlp → Unsupported URL  
2. 预览页 `get_feed_info` → 仅 `coverUrl` + `export/...`  
3. `fetch_video_profile` → 得到 `videoUrl`  
4. curl 下载 → 约 2.2MB，H.264 720×1280，时长 ~50s  
5. 作者「科技头号」，描述含台灯/AI/ongo 跳跳灯  

## 安全与合规

- 仅下载用户有权访问、且用途合法的内容（自用备份、授权素材等）
- 勿将解析到的长期 token 提交进 Git
- 勿对正式业务库/远端服务器做无关部署；本 Skill 只做本机文件下载
