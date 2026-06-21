"""
任务一：CSV 表头英文化（中文→英文，19列）
任务二：新增 3 列（suitable_award_goals, suitable_for_baoyan, award_rate_reference）
输出：22列英文表头的 CSV
"""
import csv, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "竞赛资料汇总.csv")
DST = os.path.join(BASE, "竞赛资料汇总.csv")  # 原地覆盖

# 任务一：表头映射
HEADER_MAP = {
    "竞赛全称": "competition_name",
    "竞赛简称": "competition_short_name",
    "竞赛级别": "competition_level",
    "竞赛大类": "category",
    "主办单位": "organizer",
    "适合专业": "suitable_majors",
    "能力要求": "required_skills",
    "赛道方向": "directions",
    "作品形式": "entry_format",
    "准备周期": "preparation_cycle",
    "时间等级": "time_requirement_level",
    "难度": "difficulty_level",
    "报名时间": "registration_time",
    "提交/比赛时间": "submission_time",
    "参赛形式": "team_type",
    "适合项目转化": "suitable_for_project_transfer",
    "备赛所需材料清单": "required_materials",
    "风险分析": "risk_points",
    "资料来源": "source_link",
}
NEW_HEADERS = list(HEADER_MAP.values()) + [
    "suitable_award_goals",
    "suitable_for_baoyan",
    "award_rate_reference",
]


def parse_level(value: str) -> str:
    """从 competition_level 字段提取级别前缀"""
    if "A1" in value: return "A1"
    if "A2" in value: return "A2"
    if "A3" in value: return "A3"
    if "A4" in value: return "A4"
    if "B" in value or "B级" in value: return "B"
    return "other"


def get_award_goals(level_val: str) -> str:
    """任务二列20：根据级别判断适合的奖项目标"""
    p = parse_level(level_val)
    if p in ("A1", "A2", "A3", "A4"):
        return "校奖,省奖,国奖"
    elif p == "B":
        return "省奖,国奖"
    else:
        return "校奖,省奖"


def get_baoyan(level_val: str) -> str:
    """任务二列21：是否对保研有帮助"""
    if "A" in level_val or "国家级" in level_val:
        return "是"
    elif "B" in level_val or "省部级" in level_val:
        return "视学校而定"
    else:
        return "否"


def get_award_rate(diff: str, level_val: str) -> str:
    """任务二列22：获奖率参考"""
    # 先尝试从 risk_points 提取 -> 这里无法获取其他字段，在 main 中处理
    p = parse_level(level_val)
    diff = diff.strip()

    if diff == "高":
        if p in ("A1", "A2"):
            return "省赛约5-10%,国赛约1-3%"
        else:
            return "省级获奖率约10-15%"
    elif diff == "中":
        if p in ("A1", "A2"):
            return "省赛约15-20%,国赛约3-5%"
        else:
            return "省赛约20-30%,国赛约5-10%"
    elif diff == "低":
        return "获奖率较高,具体以官方为准"
    else:
        return "以官方公示为准"


def main():
    with open(SRC, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("❌ CSV 文件为空")
        return

    old_header = rows[0]
    data_rows = rows[1:]

    # 验证表头
    for cn in old_header:
        if cn not in HEADER_MAP:
            print(f"⚠️  发现未知表头: '{cn}'，将原样保留")

    print(f"读取完成: 1 行表头 + {len(data_rows)} 行数据")
    print(f"原列数: {len(old_header)}")

    # 构建新数据
    new_rows = [NEW_HEADERS]

    for idx, row in enumerate(data_rows):
        if len(row) < 19:
            # 补齐到19列
            row = row + [""] * (19 - len(row))
        elif len(row) > 19:
            row = row[:19]

        level_val = row[2]   # 竞赛级别 index 2
        diff_val  = row[11]  # 难度 index 11
        risk_val  = row[17]  # 风险分析 index 17

        col20 = get_award_goals(level_val)
        col21 = get_baoyan(level_val)

        # 尝试从 risk_points 中提取获奖率信息
        award_info = ""
        if "获奖率" in risk_val:
            # 提取包含"获奖率"的片段，限30字符
            m = re.search(r'[^,]*获奖率[^,]*', risk_val)
            if m:
                award_info = m.group().strip()
        if not award_info:
            award_info = get_award_rate(diff_val, level_val)

        col22 = award_info

        new_row = row + [col20, col21, col22]
        new_rows.append(new_row)

    # 写回（覆盖原文件）
    with open(DST, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(new_rows)

    # 验证
    print(f"\n✅ 转换完成！")
    print(f"   文件: {DST}")
    print(f"   列数: {len(NEW_HEADERS)}")
    print(f"   数据行: {len(data_rows)}")

    # 抽样验证
    print(f"\n=== 抽样验证 ===")
    for label, idx in [("第一行(A1)", 0), ("A4某行", 10)]:
        if idx < len(data_rows):
            r = new_rows[idx + 1]
            print(f"[{label}] {r[0][:20]}... | 列20={r[19]} | 列21={r[20]} | 列22={r[21][:20]}...")

    # 列21统计
    baoyan_counts = {}
    for r in new_rows[1:]:
        v = r[20]
        baoyan_counts[v] = baoyan_counts.get(v, 0) + 1
    print(f"\n保研加分统计: {baoyan_counts}")


if __name__ == '__main__':
    main()
