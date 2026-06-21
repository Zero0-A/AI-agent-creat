"""
将 竞赛资料汇总.md 中的 Markdown 多表格转换为单个 CSV 文件。
处理要点：
  - 4个分组表格(A1/A2/A3/A4)合并为一个CSV
  - 自动识别表头行与数据行
  - 统一19列输出
  - UTF-8 BOM 确保 Excel 直接打开不乱码
  - CSV字段内逗号用双引号包裹
"""
import csv, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE, "竞赛资料汇总.md")
CSV_PATH = os.path.join(BASE, "竞赛资料汇总.csv")

# 期望的19列标题（以表格第一列表头为准，去除前后空格后统一）
EXPECTED_COLS = [
    "竞赛全称", "竞赛简称", "竞赛级别", "竞赛大类", "主办单位",
    "适合专业", "能力要求", "赛道方向", "作品形式", "准备周期",
    "时间等级", "难度", "报名时间", "提交/比赛时间", "参赛形式",
    "适合项目转化", "备赛所需材料清单", "风险分析", "资料来源"
]


def is_separator(line: str) -> bool:
    """判断是否为 Markdown 表格分隔行，如 |---|---|---|"""
    return bool(re.match(r'^\|[\s\-:|]+\|$', line.strip()))


def is_data_row(line: str) -> bool:
    """判断是否为有效数据行（以 | 开头，包含非分隔线内容）"""
    s = line.strip()
    if not s.startswith('|'):
        return False
    if is_separator(s):
        return False
    # 排除纯说明行（如 > *注：xxx）
    if s.startswith('| >'):
        return False
    return True


def parse_row(line: str) -> list[str]:
    """将 Markdown 表格行解析为字段列表"""
    s = line.strip().strip('|')
    # 按 | 分割，保留字段内的逗号等特殊字符
    cells = [c.strip() for c in s.split('|')]
    return cells


def main():
    rows = []  # 最终数据行列表
    header_found = False

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip():
                continue

            # 检测表头行（包含 竞赛全称 的行）
            if '竞赛全称' in line and '竞赛简称' in line:
                header_found = True
                continue

            # 跳过分隔线
            if is_separator(line):
                continue

            # 解析数据行
            if is_data_row(line):
                cells = parse_row(line)
                if header_found and len(cells) == 19:
                    rows.append(cells)

    # 写入CSV（UTF-8 BOM 确保Excel兼容）
    with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(EXPECTED_COLS)
        writer.writerows(rows)

    # 验证
    print(f"✅ 转换成功！")
    print(f"   源文件: {MD_PATH}")
    print(f"   输出文件: {CSV_PATH}")
    print(f"   表头: {len(EXPECTED_COLS)} 列")
    print(f"   数据行: {len(rows)} 行")
    print(f"   编码: UTF-8 BOM (Excel直接打开不乱码)")

    # 按级别统计
    level_counts = {}
    for r in rows:
        lv = r[2]  # 竞赛级别是第3列(index=2)
        key = lv.split('（')[0].strip() if '（' in lv else lv
        level_counts[key] = level_counts.get(key, 0) + 1
    for k, v in sorted(level_counts.items()):
        print(f"   {k}: {v} 行")


if __name__ == '__main__':
    main()
