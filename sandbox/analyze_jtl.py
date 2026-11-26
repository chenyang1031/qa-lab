"""JTL 结果分析:总请求数 / 错误率 / TPS / RT 百分位
用法: python analyze_jtl.py products.jtl"""
import csv
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "products.jtl"
rows = []
with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

n = len(rows)
if n == 0:
    print("结果文件为空,压测可能没跑起来")
    sys.exit(1)

errors = sum(1 for r in rows if r["success"] != "true")
elapsed = sorted(int(r["elapsed"]) for r in rows)


def pct(p):
    return elapsed[min(len(elapsed) - 1, int(len(elapsed) * p / 100))]


ts = sorted(int(r["timeStamp"]) for r in rows)
duration = max((ts[-1] - ts[0]) / 1000, 1)
tps = n / duration

print(f"总请求 {n} | 错误 {errors}({errors / n:.1%})")
print(f"测试时长 {duration:.0f} 秒 | 吞吐量 TPS ≈ {tps:.1f}/秒")
print(f"响应时间:avg={sum(elapsed)/n:.0f}ms  p50={pct(50)}ms  p90={pct(90)}ms  p95={pct(95)}ms  p99={pct(99)}ms  max={elapsed[-1]}ms")
