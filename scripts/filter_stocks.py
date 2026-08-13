"""
选股脚本：筛选股价<20元、盈利中(PE>0)、市值<=100亿的A股，取30只
并附加10只指定股票，输出逗号分隔的代码列表到stdout
错误信息输出到stderr，不影响stdout解析
"""
import sys


def log(msg):
    print(msg, file=sys.stderr)


def main():
    try:
        import akshare as ak
        import pandas as pd
    except ImportError as e:
        log(f"ERROR: 缺少依赖: {e}")
        print("")  # empty output -> fallback
        sys.exit(0)  # don't fail the workflow

    log("📊 正在获取A股实时行情数据...")

    try:
        df = ak.stock_zh_a_spot_em()
    except Exception as e:
        log(f"ERROR: 获取行情失败: {e}")
        print("")
        sys.exit(0)

    total = len(df)
    log(f"   获取到 {total} 只A股")

    if total == 0:
        log("WARNING: 获取数据为空")
        print("")
        sys.exit(0)

    # 检查列名
    log(f"   列名: {list(df.columns)[:10]}...")

    # 映射列名（兼容不同版本）
    col_map = {}
    for col in df.columns:
        if "价" in str(col) and "最新" in str(col):
            col_map["price"] = col
        if "市盈率" in str(col):
            col_map["pe"] = col
        if "总市值" in str(col):
            col_map["market_cap"] = col
        if "代码" in str(col):
            col_map["code"] = col

    log(f"   列映射: {col_map}")

    if not all(k in col_map for k in ["price", "pe", "market_cap", "code"]):
        log("ERROR: 必要列缺失")
        print("")
        sys.exit(0)

    # 转换数值
    for src, dst in [("price", "price"), ("pe", "pe"), ("market_cap", "market_cap")]:
        df[dst] = pd.to_numeric(df[col_map[src]], errors="coerce")

    # 筛选
    mask = (
        (df["price"] > 0) &
        (df["price"] < 20) &
        (df["pe"] > 0) &
        (df["market_cap"] <= 1e10)
    )

    filtered = df[mask].copy()
    log(f"   符合条件: {len(filtered)} 只")

    # 取前30只
    if len(filtered) > 0:
        filtered = filtered.sort_values("market_cap", ascending=False)
        codes = filtered[col_map["code"]].head(30).tolist()
    else:
        codes = []

    # 固定添加
    fixed = [
        "300708", "002400", "113695", "601636", "002065",
        "600550", "159807", "601969", "600596", "420063",
    ]

    seen = set()
    result = []
    for code in codes + fixed:
        if code not in seen:
            seen.add(code)
            result.append(code)

    log(f"   最终: {len(result)} 只 (筛选{len(codes)} + 固定{len(fixed)})")

    # 仅输出代码列表到stdout
    print(",".join(result))


if __name__ == "__main__":
    main()