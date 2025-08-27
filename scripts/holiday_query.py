import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pydantic import Field, BaseModel
import pendulum

from yuan.patch import MultiInputTool
from yuan.tools.utils import tool_success, tool_failure, get_format_date

# 数据源配置
PRIMARY_DATA_SOURCE = "https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"
BACKUP_DATA_SOURCE = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json"

# 缓存存储
holiday_cache = {}
cache_expiry = {}

class HolidayQueryInput(BaseModel):
    """节假日查询输入参数"""
    date: Optional[str] = Field(description="查询日期，格式：YYYY-MM-DD，不指定则查询当前日期")
    query_type: str = Field(description="查询类型：holiday_info/current_year_holidays/next_holiday/is_holiday/current_year_work_days/countdown")

def get_current_year() -> int:
    """获取当前年份"""
    return pendulum.now('Asia/Shanghai').year

def get_date_year(date_str: str) -> int:
    """从日期字符串中提取年份"""
    try:
        return int(date_str.split('-')[0])
    except:
        return get_current_year()

def fetch_holiday_data(year: int) -> Optional[Dict[str, Any]]:
    """获取指定年份的节假日数据"""
    current_time = pendulum.now('Asia/Shanghai')
    
    # 检查缓存
    if year in holiday_cache and year in cache_expiry:
        if cache_expiry[year] > current_time:
            return holiday_cache[year]
    
    # 尝试从主要数据源获取
    urls = [
        PRIMARY_DATA_SOURCE.format(year=year),
        BACKUP_DATA_SOURCE.format(year=year)
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 缓存数据，24小时过期
                holiday_cache[year] = data
                cache_expiry[year] = current_time.add(hours=24)
                return data
        except Exception as e:
            continue
    
    return None

def get_holiday_info(date_str: str) -> Dict[str, Any]:
    """获取指定日期的节假日信息"""
    try:
        year = get_date_year(date_str)
        holiday_data = fetch_holiday_data(year)
        
        if not holiday_data:
            return {"error": "无节假日数据"}
        
        # 查找指定日期的信息
        date_info = None
        for day in holiday_data.get('days', []):
            if day.get('date') == date_str:
                date_info = day
                break
        
        if date_info:
            # 根据数据结构调整字段映射
            is_holiday = date_info.get('isOffDay', False)
            holiday_name = date_info.get('name', '')
            
            return {
                "date": date_str,
                "name": holiday_name,
                "type": "holiday" if is_holiday else "work",
                "is_holiday": is_holiday,
                "is_work_day": not is_holiday,
                "note": date_info.get('note', '')
            }
        else:
            # 如果没有特殊安排，判断是否为周末
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            is_weekend = date_obj.weekday() >= 5  # 5=周六, 6=周日
            return {
                "date": date_str,
                "name": "普通日",
                "type": "normal",
                "is_holiday": is_weekend,
                "is_work_day": not is_weekend,
                "note": "周末" if is_weekend else "工作日"
            }
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def get_current_year_holidays() -> Dict[str, Any]:
    """获取当前年份所有节假日"""
    try:
        year = get_current_year()
        holiday_data = fetch_holiday_data(year)
        
        if not holiday_data:
            return {"error": "无法获取节假日数据"}
        
        # 提取所有节假日
        holidays = []
        for day in holiday_data.get('days', []):
            if day.get('isOffDay', False):  # 只获取节假日
                holidays.append({
                    "date": day.get('date'),
                    "name": day.get('name', ''),
                    "note": day.get('note', '')
                })
        
        return {
            "year": year,
            "holidays": holidays,
            "total_count": len(holidays)
        }
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def get_next_holiday() -> Dict[str, Any]:
    """获取下一个节假日"""
    try:
        current_date = pendulum.now('Asia/Shanghai').format('YYYY-MM-DD')
        current_year = get_current_year()
        
        # 获取当前年份和下一年的节假日数据
        holiday_data = fetch_holiday_data(current_year)
        next_year_data = fetch_holiday_data(current_year + 1)
        
        all_holidays = []
        
        # 处理当前年份的节假日
        if holiday_data:
            for day in holiday_data.get('days', []):
                if day.get('isOffDay', False):  # 只获取节假日
                    all_holidays.append(day)
        
        # 处理下一年的节假日
        if next_year_data:
            for day in next_year_data.get('days', []):
                if day.get('isOffDay', False):  # 只获取节假日
                    all_holidays.append(day)
        
        # 找到下一个节假日
        next_holiday = None
        for holiday in all_holidays:
            holiday_date = holiday.get('date')
            if holiday_date > current_date:
                next_holiday = holiday
                break
        
        if next_holiday:
            # 计算距离天数
            holiday_date = datetime.strptime(next_holiday['date'], '%Y-%m-%d')
            current_date_obj = datetime.strptime(current_date, '%Y-%m-%d')
            days_until = (holiday_date - current_date_obj).days
            
            return {
                "name": next_holiday.get('name', ''),
                "date": next_holiday.get('date'),
                "days_until": days_until,
                "note": next_holiday.get('note', '')
            }
        else:
            return {"error": "未找到未来的节假日"}
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def is_holiday(date_str: str) -> Dict[str, Any]:
    """判断指定日期是否为节假日"""
    try:
        holiday_info = get_holiday_info(date_str)
        if 'error' in holiday_info:
            return holiday_info
        
        return {
            "date": date_str,
            "is_holiday": holiday_info.get('is_holiday', False),
            "is_work_day": holiday_info.get('is_work_day', False),
            "type": holiday_info.get('type', 'normal'),
            "name": holiday_info.get('name', '普通日')
        }
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def get_current_year_work_days() -> Dict[str, Any]:
    """获取当前年份调休工作日安排"""
    try:
        year = get_current_year()
        holiday_data = fetch_holiday_data(year)
        
        if not holiday_data:
            return {"error": "无法获取节假日数据"}
        
        # 提取所有调休工作日
        work_days = []
        for day in holiday_data.get('days', []):
            if not day.get('isOffDay', False) and day.get('name'):  # 调休工作日
                work_days.append({
                    "date": day.get('date'),
                    "name": day.get('name', ''),
                    "note": day.get('note', '')
                })
        
        return {
            "year": year,
            "work_days": work_days,
            "total_count": len(work_days)
        }
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def get_holiday_countdown() -> Dict[str, Any]:
    """获取距离下一个节假日的天数"""
    try:
        next_holiday_info = get_next_holiday()
        if 'error' in next_holiday_info:
            return next_holiday_info
        
        return {
            "next_holiday": next_holiday_info.get('name', ''),
            "date": next_holiday_info.get('date', ''),
            "days_until": next_holiday_info.get('days_until', 0),
            "note": next_holiday_info.get('note', '')
        }
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

def _control_holiday_query(**kwargs) -> str:
    """节假日查询工具控制函数"""
    try:
        date = kwargs.get("date")
        query_type = kwargs.get("query_type", "holiday_info")
        
        # 如果没有指定日期，使用当前日期
        if not date:
            date = pendulum.now('Asia/Shanghai').format('YYYY-MM-DD')
        
        # 标准化日期格式
        if date:
            date = get_format_date(date)
        
        # 根据查询类型调用相应的函数
        if query_type == "holiday_info":
            result = get_holiday_info(date)
        elif query_type == "current_year_holidays":
            result = get_current_year_holidays()
        elif query_type == "next_holiday":
            result = get_next_holiday()
        elif query_type == "is_holiday":
            result = is_holiday(date)
        elif query_type == "current_year_work_days":
            result = get_current_year_work_days()
        elif query_type == "countdown":
            result = get_holiday_countdown()
        else:
            return tool_failure("不支持的查询类型")
        
        if 'error' in result:
            return tool_failure(result['error'])
        
        return tool_success(result)
    except Exception as e:
        return tool_failure(f"节假日查询失败: {str(e)}")

# 创建节假日查询工具
holiday_query_tool = MultiInputTool(
    name="holiday_query",
    description="中国法定节假日查询工具，支持查询节假日信息、调休安排、工作日判断等。可以查询指定日期是否为节假日，获取当前年份所有节假日，查询下一个节假日，获取调休工作日安排，以及节假日倒计时等功能。\n"
    "参数说明：\n"
    "date: 日期，格式为YYYY-MM-DD，默认当前日期\n"
    "query_type: 查询类型，可选值为holiday_info（节假日信息）、current_year_holidays（当前年份所有节假日）、next_holiday（下一个节假日）、is_holiday（指定日期是否为节假日）、current_year_work_days（当前年份调休工作日安排）、countdown（节假日倒计时）\n"
    "返回说明：\n"
    "isOffDay: true（当天休息）/false（当天调休加班）\n",
    func=_control_holiday_query,
    args_schema=HolidayQueryInput,
    return_direct=True,
    metadata={
        "settings": {
            "remove_content": False,
            "tool_return_to_client": True,
        }
    }
)