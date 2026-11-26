# Day 11 · demo 商城部署上 K8s

## K8s 四个新概念(全部用到实物上)
- **initContainer**:app 的先遣兵,`nc -z db 3306` 等数据库就绪才放行主容器
- **PVC + local-path**:MySQL 数据持久卷,容器删了数据还在
- **readinessProbe**:mysqladmin ping 通过才进负载均衡,`Running ≠ Ready`
- **NodePort 30080**:k3d LB 把宿主机 8002 映射到节点 30080

## 部署节奏(亲历)
拉镜像(加速站)→ MySQL 首次初始化(30–60 秒)→ readiness 通过 → initContainer 放行 → app 就绪

## 终极演示:双环境 12 用例全绿
compose(8001)与 K8s(8002)同一套测试(`BASE_URL` 环境变量切换)全绿 = **测试与实现解耦**的实证

## k3s→k3d 战斗记录(WSL 内核兼容性)
1. 裸 K3s on WSL:kubelet 报 "system validation failed - wrong number of fields (expected 6, got 7)"(内核 6.18 太新)
2. 迂回 k3d:K3s 装进 Docker 容器(Docker 已验证可靠),kubectl 完全一致
3. 三个 ghcr 镜像被墙:rancher/k3s 走 Docker Hub 加速站;k3d-proxy、k3d-tools 走南京大学镜像站(ghcr.nju.edu.cn)
4. 端口冲突:k3d LB 占 8001 撞 compose 应用 → 改 8002

## kubectl 五连
get / describe(Events 排障金矿)/ logs / delete / get -A
