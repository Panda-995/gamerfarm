# 使用预构建镜像

本 Fork 为 [VisaHolder/gamerfarm](https://github.com/VisaHolder/gamerfarm) 添加自动同步和 GHCR 镜像发布，应用代码沿用上游。

- 镜像：`ghcr.io/panda-995/gamerfarm:latest`
- 平台：`linux/amd64`、`linux/arm64`，Docker 自动选择适合宿主的架构。
- 每次构建另有 `sha-<12 位提交号>` 标签，可用于固定版本。
- 工作流 `.github/workflows/publish-container.yml` 每 6 小时检查并合并上游 `main`。北京时间约为 02:23、08:23、14:23、20:23，GitHub 定时任务可能延迟。
- 检查到更新后在同一次工作流中构建并发布，不依赖机器人提交再次触发工作流。也支持手动运行和推送相关源码后构建。
- 两种架构都通过实际启动及健康检查后，才更新 `latest`。
- 合并保留 Fork 的工作流和部署文件；遇到冲突直接失败，不强制覆盖。
- 工作流只使用 GitHub 自动提供的 `GITHUB_TOKEN`，无需添加个人令牌 Secret。

## Linux / NAS 部署

下载本仓库的 `docker-compose.ghcr.yml`，保存为 `compose.yaml`，并将 `.env.ghcr.example` 保存为 `.env`。

修改 `.env` 中的管理密码。`PUID` 和 `PGID` 应匹配数据目录所有者，用 `id -u`、`id -g` 查看。然后在同一目录运行：

```bash
mkdir -p config logs backups plugins
docker compose pull
docker compose up -d
```

访问 `http://服务器IP:7242`，使用设置的管理密码登录并添加 Steam 账号。账号配置、日志、备份和插件分别保存在四个挂载目录中。

仅本机访问时，将端口映射改为 `127.0.0.1:7242:7242`。需要公网或域名访问时，按上游文档设置 `GAMERFARM_PUBLIC_ADDRESS`；使用反向代理时还应设置 `GAMERFARM_TRUSTED_PROXIES`。

## 更新已部署的容器

```bash
docker compose pull
docker compose up -d
```

## 手动同步并构建

打开仓库的 **Actions → Sync upstream and publish container → Run workflow**。同步和构建均可在该次运行的日志中查看；首次发布 GHCR 包后需将包的可见性设为 Public，才能匿名拉取。
