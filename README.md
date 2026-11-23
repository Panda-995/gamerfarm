<p align="center">
  <img src="assets/overview.png" alt="gamer.farm 管理面板：查看所有账号的运行状态" width="880">
</p>

<h1 align="center">gamer.farm 中文介绍</h1>

<p align="center">
  <b>在后台管理多个 Steam 账号，自动挂卡、累计游戏时长。<br>
  常用账号可以启用人类模式，按日常作息安排游戏。</b>
</p>

<p align="center">
  <a href="https://github.com/VisaHolder/gamerfarm/releases/latest"><img src="https://img.shields.io/github/v/release/VisaHolder/gamerfarm?label=上游版本&color=8b5cf6" alt="上游最新版本"></a>
  <a href="https://github.com/Panda-995/gamerfarm/actions/workflows/publish-container.yml"><img src="https://github.com/Panda-995/gamerfarm/actions/workflows/publish-container.yml/badge.svg" alt="上游同步与双架构构建状态"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/许可证-MPL--2.0-blue" alt="MPL-2.0 许可证"></a>
</p>

<p align="center">
  <a href="https://github.com/VisaHolder/gamerfarm">上游项目</a> ·
  <a href="https://github.com/users/Panda-995/packages/container/package/gamerfarm">Docker 镜像</a> ·
  <a href="https://gamer.mom/docs">使用指南</a> ·
  <a href="https://gamer.mom/commands">命令列表</a> ·
  <a href="README.upstream.md">上游英文原文</a>
</p>

本仓库是 [VisaHolder/gamerfarm](https://github.com/VisaHolder/gamerfarm) 的 Fork，提供中文项目说明、预构建 Docker 镜像和自动上游同步。应用功能沿用上游，支持 Windows、macOS、Linux 和 Docker。

## Docker / NAS 部署

镜像地址：`ghcr.io/panda-995/gamerfarm:latest`。支持 `linux/amd64` 和 `linux/arm64`，Docker 会自动选择适合宿主机的架构。镜像已公开，拉取时无需登录 GHCR，也不需要本地编译。

将下面内容保存为 `compose.yaml`，或直接下载 [docker-compose.ghcr.yml](docker-compose.ghcr.yml)：

```yaml
services:
  gamerfarm:
    image: ghcr.io/panda-995/gamerfarm:latest
    container_name: gamerfarm
    hostname: gamerfarm
    restart: unless-stopped
    init: true
    stdin_open: true
    stop_grace_period: 1m

    user: "0:0"

    environment:
      TZ: Asia/Shanghai
      GAMERFARM_WEB_PASSWORD: "panda995"

    ports:
      - "7242:7242"

    volumes:
      - ./config:/data/config
      - ./logs:/data/logs
      - ./backups:/data/backups
      - ./plugins:/data/plugins
```

在 Compose 文件所在目录执行：

```bash
mkdir -p config logs backups plugins
docker compose up -d
```

打开 `http://你的NAS或服务器IP:7242`，输入管理密码 `panda995`，然后添加 Steam 账号。`GAMERFARM_WEB_PASSWORD` 是网页管理后台的密码，与 Steam 登录密码分别设置。

本配置使用 `user: "0:0"`，容器以 root 用户运行，便于读写 NAS 挂载的数据目录。`TZ: Asia/Shanghai` 决定人类模式作息、夜间规则和日报使用的时区。

首次进入可以选择「简体中文」；已有配置可在 **Settings → Global settings → Language** 中切换。部分尚未翻译的内容及控制台命令回复仍显示英文。

| 宿主机目录 | 保存内容 |
| --- | --- |
| `./config` | 账号、登录令牌、设置及状态 |
| `./logs` | 运行日志 |
| `./backups` | 备份和恢复前保留的副本 |
| `./plugins` | 插件及附加组件 |

更新容器：

```bash
docker compose pull
docker compose up -d
```

查看日志使用 `docker compose logs -f gamerfarm`，停止服务使用 `docker compose down`。更多配置见 [容器部署说明](CONTAINER.md)。

## 自动同步与镜像构建

[GitHub Actions 工作流](.github/workflows/publish-container.yml) 每 6 小时检查一次上游 `VisaHolder/gamerfarm` 的 `main` 分支，计划时间为北京时间 **02:23、08:23、14:23、20:23**，实际执行可能受 GitHub 调度延迟影响。

1. 同步上游代码，保留本仓库的中文 `README.md`；上游英文说明同步保存到 `README.upstream.md`。
2. 上游有新提交时，在同一次工作流中构建 `linux/amd64` 和 `linux/arm64` 镜像。
3. 检查镜像清单，并分别启动两种架构的容器，验证管理面板健康检查。
4. 全部通过后更新 `ghcr.io/panda-995/gamerfarm:latest`，同时保留 `sha-<12位提交号>` 标签，便于固定版本。

同步与构建在同一条工作流中串联，不依赖同步机器人推送后再次触发构建。工作流只使用 GitHub 提供的临时 `GITHUB_TOKEN`，无需添加个人令牌。应用代码发生合并冲突时停止同步，不强制覆盖。

推送相关代码或部署配置会触发构建；也可以在 **Actions → Sync upstream and publish container → Run workflow** 手动同步并重建。镜像发布后，已部署的 NAS 仍需执行上面的更新命令才能使用新版本。

## 主要功能

gamer.farm 登录 Steam 账号后，会逐个游戏挂卡，并估算剩余时间。卡片掉落结束后，可以继续累计指定游戏的时长，最多同时挂 32 个游戏。也可以设置自定义游戏名称，在个人资料上显示该名称，实际游戏仍累计时长。

常用账号可以开启**人类模式**：一次玩一个游戏，安排休息、吃饭、睡觉，偶尔跳过一天。最后一张卡片掉落后还会继续运行约 15～20 分钟，再按作息休息。自己开始玩游戏时，程序会暂停该账号的挂机，退出游戏几分钟后再恢复。

其他功能包括：

- **多个账号**：统一查看状态，分别设置常用账号和挂卡账号，并在自己的账号之间转移物品。
- **免费内容与活动**：领取礼物、访客通行证及促销贴纸；可选领取免费游戏和 DLC。Steam 活动期间支持队列奖励、Steam 大奖提名和投票，可用 `events` 查看记录。
- **交易管理**：接受赠送物品的报价；可选开启公平的一换一卡片交易。其他报价会编号并通知，等待 `trade accept myaccount 3` 或 `trade decline myaccount 3` 处理。
- **跨用户换卡**：按账号选择开启后，通过 gamer.mom 匹配其他用户，多余普通卡片一换一，双方都会核对交易，不拿走当前套卡需要的卡片。
- **验证器**：导入验证器的账号可在 Authenticator 页面查看 Steam Guard 验证码，确认或拒绝交易及市场上架请求。
- **账号健康检查**：查看等级、封禁、交易暂挂、市场权限、受限状态、Steam Guard 和手机号；状态变差时通知。
- **异常监测**：每 30～60 分钟检查新增 API Key、新设备、邮箱、手机号、Steam Guard 变化或全端退出等情况；发现变化会通知并暂停自动交易，等待 `scamwatch ok myaccount` 确认。
- **历史统计**：查看每日掉卡数、累计游戏时长和库存价值，以及本周与上周的变化。
- **备份恢复**：可配置每日密码加密备份，保存到指定目录；使用 `backup now` 立即备份，也可以在另一台电脑恢复。
- **通知与远程命令**：支持 Discord、Telegram；网页管理面板也适配手机。
- **成就功能**：手动开启后，按前置条件、章节、难度和时间安排逐步完成成就，可选自动挑选目标游戏。
- **软件与家庭共享**：支持累计 OBS、ShareX、Blender 等软件的使用时长，也支持 Steam 家庭共享库。
- **账号迁移**：导入 ArchiSteamFarm、Idle Master Extended、Idle Master、HourBoostr、SingleBoostr、Steam Game Idler、steam-idler 的账号和设置。
- **插件扩展**：在 Plugins 页面安装经过签名清单校验的上游附加组件，包括 [rep4rep](docs/rep4rep.md)。完整说明见 [附加组件列表](docs/addons.md)。

涉及物品和余额的功能需要分别开启。多余物品出售或转宝石、拆包或制作补充包、消费 Steam 点数、购买卡片和跨用户换卡等默认关闭；部分功能会先显示预计操作并要求确认。默认自动领取的内容为免费活动物品，以及开启相应选项后的免费游戏。

可选功能还包括按价格和数量限制处理多余卡片、背景及表情；根据卡片估值设置自动拆包条件；制作补充包、合成徽章；按保留点数和每周预算购买季节徽章等级；在每日、每周预算内购买缺失的整套卡片，或计算购买补充包是否更划算。自动领取免费游戏、自定义状态名称、备份、通知和插件等也可以按需配置。

## 下载与安装桌面版

前往[上游最新发行版](https://github.com/VisaHolder/gamerfarm/releases/latest)或 [gamer.mom](https://gamer.mom) 下载。桌面和独立运行版已包含运行环境，无需额外安装 .NET。

<p align="center">
  <img src="assets/setup.png" alt="安装界面：迁移来源、开机启动与桌面快捷方式" width="880">
</p>

Windows 提供两种文件：

- `gamer.farm-v…-setup.exe`：安装版，提供开始菜单、桌面快捷方式、开机启动和卸载入口，无需管理员权限。安装器会检查已有的挂机工具或便携版，并提供迁移选项。
- `gamer.farm-v…-portable.zip`：便携版，解压后运行 `gamerFarm.exe`，程序和数据都保存在解压目录。

macOS 提供 Apple Silicon 和 Intel 版本，解压后运行 `start.command`。Linux 提供 x64、ARM64 等独立运行包。详细步骤见[上游 Linux、Mac 与 Docker 指南](https://gamer.mom/docs#linux-mac-and-docker)。

首次打开管理面板时：

1. 选择界面语言，再选择简易或高级设置。高级设置会进一步询问手机访问、通知、更新时段和账号选项。
2. 选择账号用途。常用账号启用人类模式，备用或挂卡账号按挂卡模式运行，之后可以随时修改。
3. 添加 Steam 登录账号，按提示输入密码和 Steam Guard 验证码；也可以用 Steam 手机客户端扫码登录。
4. 根据需要选择主要游戏、作息和挂卡结束后的行为。检测到其他挂机工具时，也可以选择导入账号。

<p align="center">
  <img src="assets/walkthrough.png" alt="首次设置：选择模式、账号用途和迁移来源" width="880">
  <br><sub>首次设置支持简易流程和高级选项。</sub>
</p>

<p align="center">
  <img src="assets/walkthrough-phone.png" alt="手机上的首次设置界面" width="420">
</p>

<p align="center">
  <img src="assets/setup-existing.png" alt="已有安装的更新、迁移和卸载选项" width="880">
</p>

Windows 安装版、便携版及 Linux/macOS 独立运行版支持程序内更新。点击管理面板的 Update，或执行 `update accept`；也可配置等待账号休息时更新，或在夜间自动更新。`update now` 会立即更新。Docker 部署通过拉取镜像并重新创建容器更新。

## 界面预览

<p align="center">
  <img src="assets/accounts.png" alt="账号页面：运行状态、剩余卡片和对外展示状态" width="880">
  <br><sub>账号页面集中显示每个账号的状态和剩余卡片。</sub>
</p>

<p align="center">
  <img src="assets/history.png" alt="每日掉卡数、游戏时长与库存价值历史" width="880">
</p>

<p align="center">
  <img src="assets/settings.png" alt="人类模式的游戏和日常作息设置" width="880">
</p>

<p align="center">
  <img src="assets/authenticator.png" alt="验证器页面：验证码和待确认事项" width="880">
</p>

<p align="center">
  <img src="assets/console.png" alt="控制台：输入命令并查看回复" width="880">
</p>

## 手机访问

Phone 页面提供局域网和外网访问二维码，并检查管理密码、网络访问、防火墙和路由器配置。iPhone 可以通过 Safari 的「添加到主屏幕」创建入口；Android 可以使用浏览器中的相同功能。通知可通过 Telegram 或 Discord 接收。

Docker 部署使用本文配置后，可在局域网访问 `http://服务器IP:7242`。若希望页面显示正确的手机访问链接和二维码，可以增加 `GAMERFARM_HOME_ADDRESS`，值为服务器的局域网 IP。

公网访问需要按[上游远程访问指南](https://gamer.mom/docs#on-a-vps-a-rented-server)配置 `GAMERFARM_PUBLIC_ADDRESS`；反向代理场景还需设置 `GAMERFARM_TRUSTED_PROXIES`。上游外网访问功能要求至少 12 位管理密码，本文默认密码 `panda995` 用于局域网部署示例。

<p align="center">
  <img src="assets/phone.png" alt="手机页面：局域网、外网访问链接与二维码" width="880">
</p>

## 迷你模式

桌面版点击 **mini** 或输入 `mini`，可缩小为账号状态面板，显示账号当前任务、开始或停止按钮，以及掉卡进度。账号较多时可以展开分页；需要处理的账号会置顶提示。支持窗口置顶和切回完整界面。

<p align="center">
  <img src="assets/mini-mode.png" alt="迷你模式：账号状态与挂卡进度" width="680">
</p>

## 常用命令

在管理面板的 Console 页面输入以下命令，也可以在桌面程序窗口中输入。通过 Steam 聊天发送命令的方式见[上游指南](https://gamer.mom/docs#commands-by-steam-chat)。

| 命令 | 作用 |
| --- | --- |
| `status` | 查看所有账号当前状态。 |
| `add myaccount mylogin human` | 添加账号；`human` 为人类模式，`robot` 为挂卡模式。 |
| `start myaccount` / `stop myaccount` | 登录或退出指定账号，`all` 表示全部账号。 |
| `pause myaccount 60` | 暂停 60 分钟，之后继续运行。 |
| `cards` | 查看剩余卡片及预计挂卡时间。 |
| `drops myaccount` | 立即开始挂卡，完成后恢复原来的安排。 |
| `play myaccount 730, 440` | 为挂卡账号指定游戏；人类模式在设置中选择游戏。 |
| `gamename myaccount gamer.mom` | 自定义个人资料中显示的游戏名称。 |
| `human myaccount week` | 查看该账号一周的人类模式安排。 |
| `value` | 查看各账号库存估值。 |
| `match` | 检查自己的账号之间能否互换多余卡片，`match do` 执行交易。 |
| `spare preview myaccount` | 预览多余物品出售或转宝石的操作。 |
| `levelup myaccount 50` | 估算升级至 Steam 50 级的成本。 |
| `offers` | 查看等待处理的交易报价。 |
| `scamwatch` / `health` | 查看异常监测结果及账号健康状态。 |
| `backup now` | 立即创建备份；`backup status` 查看下次备份时间。 |
| `dashboard` | 显示管理面板的本机、局域网及已配置的外网地址。 |
| `update accept` | 独立运行版安装最新更新；`update now` 立即更新，Docker 版使用镜像更新。 |
| `help` | 查看命令帮助；`help <命令或设置>` 查看具体说明。 |

完整列表见[上游命令文档](https://gamer.mom/commands)。

## 人类模式

在账号的 **Settings → Human mode** 中开启，或执行 `set myaccount LegitMode true`。程序会按设定选择主要游戏和其他游戏，安排游戏时长、休息、吃饭与睡眠，也会偶尔休息一天。交易、礼物和好友请求按相应延迟处理。还可以设置在指定日期前累计某个游戏的目标时长。

`selfcheck` 会检查人类模式的配置，并提示可以调整的选项。备用账号不启用人类模式时，会按挂卡模式持续运行。

## 数据、联网与使用边界

账号、登录令牌、验证器和日志保存在运行程序的电脑或服务器上。首次登录后通常使用保存的 Steam 登录令牌，不必每次输入密码。Windows 的凭据保护与当前用户关联；Linux 使用数据目录中的密钥加密。

程序连接 Steam，并默认每 2 小时检查一次 GitHub 更新，可在设置中调整或关闭。Discord、Telegram、rep4rep、SteamSpy 等服务在开启相应功能后使用。

程序还会按上游统计机制定期联系 gamer.mom：每小时报告随机安装 ID、版本、平台和已登录账号数量；约每 6 小时附带游戏时长、掉卡、宝石、徽章、拆包和出售数量等汇总。可通过 **Share my farming totals** 关闭汇总分享，通过 **Count me as a user** 关闭此类统计。开启低价套卡购买时，也可能分享市场最低套卡价格，可单独关闭对应分享选项。

自己在 Steam 客户端启动游戏时，程序会暂停该账号挂机。常用账号可开启 **I also use this account in my own Steam app**，避免程序修改好友与聊天在线状态。

上游说明提醒：Steam 账号自动化存在违反平台协议、账号受限或封禁的风险，人类模式并不保证账号安全。请在使用前了解上游说明及 Steam 的相关规则。

## 常见问题

**界面支持中文吗？** 支持简体中文。首次设置可选中文，之后在全局设置的 Language 中修改。

**后台登录密码是什么？** 本文 Compose 设置为 `panda995`，它只是网页管理密码。Steam 账号在管理页面另外添加。

**容器一直重启怎么办？** 先执行 `docker compose logs --tail=100 gamerfarm`。若出现 `Permission denied` 或 `can't write to /data/config as uid 1000`，检查实际使用的 Compose 是否已设置本文的 `user: "0:0"`，并确认挂载目录可以写入。

**自己还能玩游戏吗？** 可以。该账号开始游戏后，程序暂停挂机，退出游戏几分钟后恢复。

**可以管理多少个账号？** 上游没有设定固定账号数量限制，程序会依次登录；实际容量取决于机器和使用方式。

**需要每次输入 Steam 密码吗？** 通常只需首次登录，或直接用 Steam 手机客户端扫码。

**如何从其他挂机工具迁移？** 在首次设置中选择来源，或在 Accounts 页面使用 Import from another idler。程序先显示检测结果，再由你确认导入，并分别选择人类模式或挂卡模式。先停止旧工具，避免同时登录同一账号。ASF 的登录令牌和验证器也支持迁移，详见[迁移指南](https://gamer.mom/docs#coming-from-another-idler)。

**设置选项为什么很少？** 默认显示常用选项，勾选 Show advanced 可查看运行时序、挂卡顺序、管理端口和密码等高级设置。

**提示 Steam 限流怎么办？** 程序会等待后重试，频繁重启可能加重请求压力。

**配置在哪里？** Docker 版在挂载的 `./config`；Windows 安装版默认在 `%LOCALAPPDATA%\Programs\gamer.farm\config`，便携版在解压目录。可以使用程序内的加密备份与恢复功能迁移数据。

**可以放在 VPS 上吗？** 可以。使用 Docker 或 Linux 独立运行包即可，访问方式见[上游 VPS 指南](https://gamer.mom/docs#on-a-vps-a-rented-server)。

**能否让多个账号加入 Steam 群组？** 在全局设置的 Groups every account joins 中填写群组链接，也可执行 `joingroup all <链接>`。只支持无需审批的开放群组。

**遇到其他问题怎么办？** 在 Log 页面或 Docker 日志中查看具体错误，再到[上游 Issues](https://github.com/VisaHolder/gamerfarm/issues)反馈，并注意隐藏账号凭据。

## 开发与更多文档

- [使用指南](https://gamer.mom/docs)：首次设置、各项功能和设置说明，本仓库也保留了 [docs/](docs/README.md)。
- [附加组件](docs/addons.md)：上游附加组件说明及[签名清单](addons/addons.json)。
- [插件开发](https://gamer.mom/plugins)：用 C# 扩展命令和功能。
- [上游英文项目介绍](README.upstream.md)：自动同步时更新，便于查阅上游最新说明。

自行编译需要 [.NET 10 SDK](https://dotnet.microsoft.com/download)：

```bash
git clone https://github.com/Panda-995/gamerfarm.git
cd gamerfarm
dotnet publish src/GamerFarm -c Release -o run
```

Windows 运行 `run\gamerFarm.exe`；Linux/macOS 可使用对应平台的发行包，或按上游指南构建。

## 许可证与致谢

项目采用 [Mozilla Public License 2.0](LICENSE)。可以使用、Fork 和商业分发；插件可以使用其他许可证，包括闭源许可证。修改并分发 gamer.farm 自身文件时，需要按许可证公开对应修改。

应用由上游作者开发，基于 [SteamKit2](https://github.com/SteamRE/SteamKit)。本 Fork 维护中文介绍、部署配置和自动镜像构建，完整英文说明见 [README.upstream.md](README.upstream.md)。
