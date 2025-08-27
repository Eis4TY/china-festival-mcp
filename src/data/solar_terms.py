"""二十四节气数据"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# 二十四节气名称
SOLAR_TERMS = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
]

# 节气对应的月份（大致）
SOLAR_TERM_MONTHS = {
    "小寒": 1, "大寒": 1, "立春": 2, "雨水": 2,
    "惊蛰": 3, "春分": 3, "清明": 4, "谷雨": 4,
    "立夏": 5, "小满": 5, "芒种": 6, "夏至": 6,
    "小暑": 7, "大暑": 7, "立秋": 8, "处暑": 8,
    "白露": 9, "秋分": 9, "寒露": 10, "霜降": 10,
    "立冬": 11, "小雪": 11, "大雪": 12, "冬至": 12
}

# 节气的大致日期（基于平均值）
SOLAR_TERM_DATES = {
    "小寒": (1, 6), "大寒": (1, 20), "立春": (2, 4), "雨水": (2, 19),
    "惊蛰": (3, 6), "春分": (3, 21), "清明": (4, 5), "谷雨": (4, 20),
    "立夏": (5, 6), "小满": (5, 21), "芒种": (6, 6), "夏至": (6, 21),
    "小暑": (7, 7), "大暑": (7, 23), "立秋": (8, 8), "处暑": (8, 23),
    "白露": (9, 8), "秋分": (9, 23), "寒露": (10, 8), "霜降": (10, 23),
    "立冬": (11, 7), "小雪": (11, 22), "大雪": (12, 7), "冬至": (12, 22)
}

def get_solar_term_for_date(year: int, month: int, day: int) -> Optional[str]:
    """获取指定日期的节气"""
    target_date = datetime(year, month, day)
    
    # 查找最接近的节气
    closest_term = None
    min_diff = float('inf')
    
    for term, (term_month, term_day) in SOLAR_TERM_DATES.items():
        try:
            term_date = datetime(year, term_month, term_day)
            diff = abs((target_date - term_date).days)
            
            # 如果在节气日期的前后3天内，认为是该节气
            if diff <= 3 and diff < min_diff:
                min_diff = diff
                closest_term = term
        except ValueError:
            continue
    
    return closest_term

def get_solar_terms_for_month(year: int, month: int) -> List[Tuple[str, int]]:
    """获取指定月份的所有节气"""
    terms = []
    
    for term, (term_month, term_day) in SOLAR_TERM_DATES.items():
        if term_month == month:
            terms.append((term, term_day))
    
    return sorted(terms, key=lambda x: x[1])

def get_next_solar_term(year: int, month: int, day: int) -> Optional[Tuple[str, datetime]]:
    """获取下一个节气"""
    current_date = datetime(year, month, day)
    
    # 查找当年剩余的节气
    next_terms = []
    
    for term, (term_month, term_day) in SOLAR_TERM_DATES.items():
        try:
            term_date = datetime(year, term_month, term_day)
            if term_date > current_date:
                next_terms.append((term, term_date))
        except ValueError:
            continue
    
    if next_terms:
        next_terms.sort(key=lambda x: x[1])
        return next_terms[0]
    
    # 如果当年没有剩余节气，返回下一年的第一个节气
    try:
        next_year_first = datetime(year + 1, 1, 6)  # 小寒
        return ("小寒", next_year_first)
    except ValueError:
        return None

def get_season_by_solar_term(term: str) -> str:
    """根据节气获取季节"""
    spring_terms = ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨"]
    summer_terms = ["立夏", "小满", "芒种", "夏至", "小暑", "大暑"]
    autumn_terms = ["立秋", "处暑", "白露", "秋分", "寒露", "霜降"]
    winter_terms = ["立冬", "小雪", "大雪", "冬至", "小寒", "大寒"]
    
    if term in spring_terms:
        return "春季"
    elif term in summer_terms:
        return "夏季"
    elif term in autumn_terms:
        return "秋季"
    elif term in winter_terms:
        return "冬季"
    else:
        return "未知"