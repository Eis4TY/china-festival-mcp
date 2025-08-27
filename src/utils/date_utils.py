"""日期处理工具模块"""

import re
from datetime import datetime
from typing import Optional, Tuple


def validate_date(date_str: str) -> bool:
    """验证日期格式是否正确
    
    Args:
        date_str: 日期字符串，格式：YYYY-MM-DD
    
    Returns:
        是否为有效日期格式
    """
    if not date_str:
        return False
    
    # 检查格式
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def format_date(date_input: str) -> str:
    """格式化日期字符串
    
    Args:
        date_input: 输入的日期字符串
    
    Returns:
        格式化后的日期字符串 YYYY-MM-DD
    
    Raises:
        ValueError: 日期格式错误
    """
    if not date_input:
        return datetime.now().strftime('%Y-%m-%d')
    
    # 尝试多种日期格式
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y.%m.%d',
        '%Y%m%d'
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_input, fmt)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    raise ValueError(f"无效的日期格式: {date_input}")


def get_current_date() -> str:
    """获取当前日期
    
    Returns:
        当前日期字符串 YYYY-MM-DD
    """
    return datetime.now().strftime('%Y-%m-%d')


def parse_date_components(date_str: str) -> Tuple[int, int, int]:
    """解析日期字符串为年月日组件
    
    Args:
        date_str: 日期字符串 YYYY-MM-DD
    
    Returns:
        (年, 月, 日) 元组
    
    Raises:
        ValueError: 日期格式错误
    """
    if not validate_date(date_str):
        raise ValueError(f"无效的日期格式: {date_str}")
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.year, date_obj.month, date_obj.day


def get_year_from_date(date_str: str) -> int:
    """从日期字符串中提取年份
    
    Args:
        date_str: 日期字符串
    
    Returns:
        年份
    """
    try:
        year, _, _ = parse_date_components(date_str)
        return year
    except ValueError:
        return datetime.now().year


def get_weekday(year: int, month: int, day: int) -> dict:
    """根据公历日期计算星期几
    
    Args:
        year: 年份
        month: 月份 (1-12)
        day: 日期 (1-31)
    
    Returns:
        包含星期信息的字典，格式：
        {
            "weekday_number": 1,  # 星期数字 (1=星期一, 7=星期日)
            "weekday_name_zh": "星期一",  # 中文星期名称
            "weekday_name_en": "Monday",  # 英文星期名称
            "date": "2024-01-01"  # 日期字符串
        }
    
    Raises:
        ValueError: 日期无效
    """
    try:
        # 创建日期对象
        date_obj = datetime(year, month, day)
        
        # 获取星期几 (0=星期一, 6=星期日)
        weekday_index = date_obj.weekday()
        
        # 转换为1-7格式 (1=星期一, 7=星期日)
        weekday_number = weekday_index + 1
        
        # 中文星期名称映射
        weekday_names_zh = {
            1: "星期一",
            2: "星期二", 
            3: "星期三",
            4: "星期四",
            5: "星期五",
            6: "星期六",
            7: "星期日"
        }
        
        # 英文星期名称映射
        weekday_names_en = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday", 
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }
        
        return {
            "weekday_number": weekday_number,
            "weekday_name_zh": weekday_names_zh[weekday_number],
            "weekday_name_en": weekday_names_en[weekday_number],
            "date": date_obj.strftime('%Y-%m-%d')
        }
        
    except ValueError as e:
        raise ValueError(f"无效的日期: {year}-{month:02d}-{day:02d}, 错误: {str(e)}")