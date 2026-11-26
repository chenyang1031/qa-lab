# Day 10 · GitHub Actions 质量门禁

## 工作流五步职责
checkout 取代码 → setup-python 装 3.11 → pip 装依赖 → 后台起被测服务 + 等就绪(30 秒探测循环) → pytest 12 条

## 红/绿实验证明了什么
- 红(故意把 404 断言改成 500 被拦)= 门禁能**发现**坏代码
- 绿(还原后通过)= 门禁能**放行**好代码
- 四条 runs = 配置错失败 → 修复成功 → 故意破坏 → 还原,完整生命周期证据链

## 解耦要点(CI 里的 MySQL 不是我电脑那个)
测试只认"127.0.0.1:8001 的接口契约",不关心数据库跑在哪——测试与实现解耦,
所以 CI 能在陌生机器上跑我的测试。

## 排障记录(两连)
1. 第 1 次运行失败:requirements.txt 在 demo-shop 子目录,CI 工作目录在仓库根 → `defaults.working-directory: demo-shop` 解决
2. 推 workflow 文件被拒:gh 凭证缺 workflow scope → `gh auth refresh -s workflow` 重新授权

## 金句
质量门禁 = 自动门:红灯发现坏代码,绿灯放行好代码,每次 push 都是给门禁喂新代码。
