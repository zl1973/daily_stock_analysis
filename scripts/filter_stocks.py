"""
选股脚本：筛选股价<20元、盈利中(PE>0)、市值<=100亿的A股，取30只
并附加10只指定股票，输出逗号分隔的代码列表
"""
import sys
import warnings

warnings.filterwarnings("ignore")


def main():
    try:
        import akshare as ak
        import pandas as pd
    except ImportError:
        print("ERROR: akshare not installed", file=sys.stderr)
        sys.exit(1)

    print("📊 正在获取A股实时行情数据...", file=sys.stderr)

    # 获取所有A股实时行情
    df = ak.stock_zh_a_spot_em()
    total_count = len(df)
    print(f"   获取到 {total_count} 只A股", file=sys.stderr)

    # 确保数值列
    df["price"] = pd.to_numeric(df["最新价"], errors="coerce")
    df["pe"] = pd.to_numeric(df["市盈率-动态"], errors="coerce")
    df["market_cap"] = pd.to_numeric(df["总市值"], errors="coerce")

    # 筛选条件
    mask = (
        (df["price"] > 0) &          # 有效价格
        (df["price"] < 20) &         # 股价 < 20元
        (df["pe"] > 0) &             # 盈利中（PE > 0）
        (df["market_cap"] <= 1e10)   # 市值 <= 100亿 (1e10 = 100亿)
    )

    filtered = df[mask].copy()
    print(f"   符合条件: {len(filtered)} 只", file=sys.stderr)

    if len(filtered) == 0:
        print("WARNING: 没有符合条件的股票，使用空列表", file=sys.stderr)
        filtered_codes = []
    else:
        # 按市值降序排列，取前30只
        filtered = filtered.sort_values("market_cap", ascending=False)
        filtered_codes = filtered["代码"].head(30).tolist()

    # 固定添加的10只股票
    fixed_stocks = [
        "300708", "002400", "113695", "601636", "002065",
        "600550", "159807", "601969", "600596", "420063",
    ]

    # 合并并去重（保持顺序）
    seen = set()
    result = []
    for code in filtered_codes + fixed_stocks:
        if code not in seen:
            seen.add(code)
            result.append(code)

    print(f"   最终股票数: {len(result)} 只", file=sys.stderr)
    print(f"   筛选: {len(filtered_codes)} 只 + 固定: {len(fixed_stocks)} 只", file=sys.stderr)

    # 输出逗号分隔的代码列表（stdout）
    print(",".join(result))


if __name__ == "__main__":
    main()