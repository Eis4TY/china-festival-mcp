"""八字（四柱）计算模块"""

from datetime import datetime
from typing import Dict, Tuple, List

# 天干
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 生肖
ZODIAC = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 时辰对应表
HOUR_TO_DIZHI = {
    (23, 1): "子", (1, 3): "丑", (3, 5): "寅", (5, 7): "卯",
    (7, 9): "辰", (9, 11): "巳", (11, 13): "午", (13, 15): "未",
    (15, 17): "申", (17, 19): "酉", (19, 21): "戌", (21, 23): "亥"
}

# 月份地支对应表（以节气为准，这里简化处理）
MONTH_TO_DIZHI = {
    1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
    7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"
}

def get_year_ganzhi(year: int) -> str:
    """计算年柱干支"""
    # 以甲子年（1984年）为基准
    base_year = 1984
    offset = (year - base_year) % 60
    
    tian_gan_index = offset % 10
    di_zhi_index = offset % 12
    
    return TIAN_GAN[tian_gan_index] + DI_ZHI[di_zhi_index]

def get_month_ganzhi(year: int, month: int) -> str:
    """计算月柱干支"""
    # 月干的计算：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚上起，丁壬壬寅顺水流，戊癸之年甲寅起
    year_gan = get_year_ganzhi(year)[0]
    
    # 年干对应的月干起始
    month_gan_start = {
        "甲": 2, "己": 2,  # 丙
        "乙": 4, "庚": 4,  # 戊
        "丙": 6, "辛": 6,  # 庚
        "丁": 8, "壬": 8,  # 壬
        "戊": 0, "癸": 0   # 甲
    }
    
    start_index = month_gan_start.get(year_gan, 0)
    month_gan_index = (start_index + month - 1) % 10
    month_zhi_index = (month + 1) % 12  # 寅月为正月
    
    return TIAN_GAN[month_gan_index] + DI_ZHI[month_zhi_index]

def get_day_ganzhi(year: int, month: int, day: int) -> str:
    """计算日柱干支"""
    # 使用公历日期计算日干支
    # 以1900年1月1日为甲戌日作为基准
    base_date = datetime(1900, 1, 1)
    target_date = datetime(year, month, day)
    
    days_diff = (target_date - base_date).days
    
    # 1900年1月1日是甲戌日，甲=0，戌=10
    base_gan = 0  # 甲
    base_zhi = 10  # 戌
    
    day_gan_index = (base_gan + days_diff) % 10
    day_zhi_index = (base_zhi + days_diff) % 12
    
    return TIAN_GAN[day_gan_index] + DI_ZHI[day_zhi_index]

def get_hour_ganzhi(day_gan: str, hour: int) -> str:
    """计算时柱干支"""
    # 确定时辰地支
    hour_zhi = None
    for (start, end), zhi in HOUR_TO_DIZHI.items():
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            hour_zhi = zhi
            break
    
    if not hour_zhi:
        hour_zhi = "子"  # 默认子时
    
    # 时干的计算：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
    hour_gan_start = {
        "甲": 0, "己": 0,  # 甲
        "乙": 2, "庚": 2,  # 丙
        "丙": 4, "辛": 4,  # 戊
        "丁": 6, "壬": 6,  # 庚
        "戊": 8, "癸": 8   # 壬
    }
    
    start_index = hour_gan_start.get(day_gan, 0)
    hour_zhi_index = DI_ZHI.index(hour_zhi)
    hour_gan_index = (start_index + hour_zhi_index) % 10
    
    return TIAN_GAN[hour_gan_index] + hour_zhi

def calculate_bazi(year: int, month: int, day: int, hour: int = 12) -> Dict[str, str]:
    """计算完整的八字"""
    year_ganzhi = get_year_ganzhi(year)
    month_ganzhi = get_month_ganzhi(year, month)
    day_ganzhi = get_day_ganzhi(year, month, day)
    hour_ganzhi = get_hour_ganzhi(day_ganzhi[0], hour)
    
    # 获取生肖
    zodiac_index = (year - 4) % 12
    zodiac = ZODIAC[zodiac_index]
    
    return {
        "year_pillar": year_ganzhi,
        "month_pillar": month_ganzhi,
        "day_pillar": day_ganzhi,
        "hour_pillar": hour_ganzhi,
        "eight_characters": f"{year_ganzhi} {month_ganzhi} {day_ganzhi} {hour_ganzhi}",
        "zodiac": zodiac,
        "year_gan": year_ganzhi[0],
        "year_zhi": year_ganzhi[1],
        "month_gan": month_ganzhi[0],
        "month_zhi": month_ganzhi[1],
        "day_gan": day_ganzhi[0],
        "day_zhi": day_ganzhi[1],
        "hour_gan": hour_ganzhi[0],
        "hour_zhi": hour_ganzhi[1]
    }

def get_wuxing_for_ganzhi(ganzhi: str) -> Dict[str, str]:
    """获取干支对应的五行"""
    wuxing_gan = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    
    wuxing_zhi = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
        "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    
    if len(ganzhi) == 2:
        gan, zhi = ganzhi[0], ganzhi[1]
        return {
            "gan_wuxing": wuxing_gan.get(gan, "未知"),
            "zhi_wuxing": wuxing_zhi.get(zhi, "未知")
        }
    
    return {"gan_wuxing": "未知", "zhi_wuxing": "未知"}