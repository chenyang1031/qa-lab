# Day 1 · 环境搭建:Docker + WSL2 + Git/GitHub

> 当天目标:环境点火。实际成果:Docker 双层验证通过、Ubuntu 账号就绪、qa-lab 仓库上线、README 推上 GitHub。

## 一、Docker Desktop 初识

- 界面:Containers(容器=跑起来的服务)/ Images(镜像=安装包);**左下角 Engine running = 引擎就绪**
- Sign in 可跳过、通知和自动更新忽略
- 机器上有旧容器(redis-easytest、api_automation 等)——**不删不动**;注意 redis-easytest 映射了 6379 端口,以后起新 Redis 前确认它没在运行

## 二、hello-world 与 Docker 原理

`docker run --rm hello-world` 的输出四步 = Docker 工作原理(面试开场就能讲):

1. Docker 客户端联系 daemon
2. daemon 从 Docker Hub 拉取镜像
3. daemon 用镜像创建容器并运行
4. 容器的输出流回客户端

## 三、WSL2 Ubuntu 初始化(踩坑最多的一天)

| 坑 | 现象 | 解决 |
|---|---|---|
| WSL 引导 username bug | 反复输入合法用户名 chenyang 仍报 `Invalid username` | 新版 WSL 引导会把回车符算进用户名。绕过:Ctrl+C 终止引导,以 root 执行一条命令建号(见下) |
| WSL 里 docker 不可用 | `command 'docker' could not be found in this WSL 2 distro` | Docker Desktop → Settings → Resources → WSL Integration → 打开 Ubuntu-22.04 → 重启 Docker Desktop,重开终端 |

建号命令(最终生效版,以后帮同事装环境可直接复用):

```bash
wsl -d Ubuntu-22.04 -u root -- bash -c \
"useradd -m -s /bin/bash -G sudo chenyang && printf '[user]\ndefault=chenyang\n' > /etc/wsl.conf && echo BUILD_OK"
```

关键点:`/etc/wsl.conf` 里 `[user] default=chenyang` 把默认登录用户写死,重启实例后引导不再出现。

## 四、"两层世界"概念(今天最重要的认知)

- `wsl -d Ubuntu-22.04` 是 **Windows 命令**,只能在 PowerShell 里敲(在 Ubuntu 里敲会报 command not found)
- `mkdir ~/xxx`、`git`、`python3` 是 **Linux 命令**,必须进 Ubuntu 里敲
- 分不清时看提示符:`PS C:\Users\xxx>` = Windows;`chenyang@机器名:~$` = Ubuntu

## 五、Git + GitHub 全链路

| 步骤 | 命令/操作 | 备注 |
|---|---|---|
| 仓库初始化 | `git init` | hint 提示默认分支叫 master → 配置 `init.defaultBranch main` + `git branch -m main`,与 GitHub 保持一致 |
| 身份配置 | `git config --global user.name / user.email` | 提交署名 |
| 注册 GitHub | github.com 注册,用户名 chenyang1031 | — |
| 建远端仓库 | 网页右上角 + → New repository → Public → 不勾任何初始化选项 | — |
| CLI 登录 | `gh auth login --hostname github.com --web` | 本机 gh 是老版本,没有 --git-protocol 参数 |
| 设备码授权 | 复制一次性码 → 手动打开 github.com/login/device → 粘贴 → Authorize | WSL 里 gh 打不开浏览器(`xdg-open` 不存在)属正常,手动开 URL 即可 |
| 凭证接通 | **`gh auth setup-git`** | 关键一步:GitHub 拒收账号密码推送,git 必须接 gh 的 OAuth 凭证,否则 push 要密码且必失败 |
| 关联 + 首推 | `git remote add origin https://github.com/chenyang1031/qa-lab.git` → `git push -u origin main` | 远端仓库网页上已建过,报 Name already exists 属正常,手动关联即可 |

## 六、Day 1 验收回顾

- [x] hello-world 跑通,能讲 Docker 四步原理
- [x] Ubuntu 提示符 chenyang@...,docker --version 双层可用
- [x] GitHub 仓库上线,README 可见
- [x] 认识三个新概念:端口映射预告(6379:6379)、命令的两层归属、token/OAuth 凭证
