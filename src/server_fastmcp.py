"""基于FastMCP的中国节假日MCP服务器

根据官方文档最佳实践重构的服务器实现。
使用FastMCP简化开发，提供更好的开发体验。
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

# 导入工具函数
try:
    from .utils.logger import setup_logger
    from .utils.date_utils import get_weekday
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)
    
    def get_weekday(year, month, day):
        date_obj = datetime(year, month, day)
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {'weekday_name_en': weekdays[date_obj.weekday()]}

# 设置日志
logger = setup_logger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("中国节假日MCP服务器")

# 数据源配置
PRIMARY_DATA_SOURCE = "https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"
BACKUP_DATA_SOURCE = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json"

# 简单的内存缓存
_holiday_cache: Dict[int, Dict[str, Any]] = {}

async def fetch_holiday_data(year: int) -> Optional[Dict[str, Any]]:
    """获取指定年份的节假日数据"""
    # 检查缓存
    if year in _holiday_cache:
        return _holiday_cache[year]
    
    # 数据源列表
    urls = [
        PRIMARY_DATA_SOURCE.format(year=year),
        BACKUP_DATA_SOURCE.format(year=year)
    ]
    
    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # 缓存数据
                    _holiday_cache[year] = data
                    return data
            except Exception as e:
                logger.warning(f"从{url}获取数据失败: {e}")
                continue
    
    logger.error(f"无法获取{year}年节假日数据")
    return None

@mcp.tool()
async def holiday_info(date: str = None) -> str:
    """查询指定日期的节假日信息，包含是否为节假日的判断
    
    Args:
        date: 查询日期，格式：YYYY-MM-DD，不指定则查询当前日期
    
    Returns:
        包含节假日信息的JSON字符串
    """
    try:
        # 如果没有提供日期，使用当前日期
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        # 获取星期几信息
        try:
            weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_index = date_obj.weekday()
            weekday_name_en = weekdays_en[weekday_index]
        except Exception as e:
            weekday_name_en = ''
            logger.warning(f"获取星期几信息失败: {e}")
        
        year = int(date.split('-')[0])
        holiday_data = await fetch_holiday_data(year)
        
        if not holiday_data:
            return '{"error": "无法获取节假日数据"}'
        
        # 查找指定日期的信息
        date_info = None
        for day in holiday_data.get('days', []):
            if day.get('date') == date:
                date_info = day
                break
        
        if date_info:
            is_holiday = date_info.get('isOffDay', False)
            holiday_name = date_info.get('name', '')
            
            result = {
                "date": date,
                "name": holiday_name,
                "type": "holiday" if is_holiday else "work",
                "is_holiday": is_holiday,
                "is_work_day": not is_holiday,
                "note": date_info.get('note', ''),
                "weekday_name_en": weekday_name_en
            }
        else:
            # 如果没有特殊安排，判断是否为周末
            is_weekend = date_obj.weekday() >= 5  # 5=周六, 6=周日
            result = {
                "date": date,
                "name": "普通日",
                "type": "normal",
                "is_holiday": is_weekend,
                "is_work_day": not is_weekend,
                "note": "周末" if is_weekend else "工作日",
                "weekday_name_en": weekday_name_en
            }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"查询节假日信息失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'  

@mcp.tool()
async def current_year_holidays() -> str:
    """获取当前年份所有法定节假日
    
    Returns:
        包含当前年份所有节假日的JSON字符串
    """
    try:
        current_year = datetime.now().year
        holiday_data = await fetch_holiday_data(current_year)
        
        if not holiday_data:
            return '{"error": "无法获取节假日数据"}'
        
        holidays = []
        for day in holiday_data.get('days', []):
            if day.get('isOffDay', False) and day.get('name'):
                # 获取星期几信息
                try:
                    date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
                    weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_index = date_obj.weekday()
                    weekday_name_en = weekdays_en[weekday_index]
                except Exception:
                    weekday_name_en = ''
                
                holidays.append({
                    "date": day['date'],
                    "name": day['name'],
                    "note": day.get('note', ''),
                    "weekday_name_en": weekday_name_en
                })
        
        result = {
            "year": current_year,
            "holidays": holidays,
            "total_count": len(holidays)
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取当前年份节假日失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'  

@mcp.tool()
async def next_holiday() -> str:
    """获取距离当前日期最近的下一个节假日
    
    Returns:
        包含下一个节假日信息的JSON字符串
    """
    try:
        today = datetime.now().date()
        current_year = today.year
        
        # 先查找当前年份的节假日
        holiday_data = await fetch_holiday_data(current_year)
        if not holiday_data:
            return '{"error": "无法获取节假日数据"}'
        
        next_holiday_info = None
        
        # 查找当前年份的下一个节假日
        for day in holiday_data.get('days', []):
            if day.get('isOffDay', False) and day.get('name'):
                holiday_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
                if holiday_date > today:
                    next_holiday_info = day
                    break
        
        # 如果当前年份没有找到，查找下一年的第一个节假日
        if not next_holiday_info:
            next_year_data = await fetch_holiday_data(current_year + 1)
            if next_year_data:
                for day in next_year_data.get('days', []):
                    if day.get('isOffDay', False) and day.get('name'):
                        next_holiday_info = day
                        break
        
        if not next_holiday_info:
            return '{"error": "未找到下一个节假日"}'
        
        # 计算距离天数
        holiday_date = datetime.strptime(next_holiday_info['date'], "%Y-%m-%d").date()
        days_until = (holiday_date - today).days
        
        # 获取星期几信息
        try:
            weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_index = holiday_date.weekday()
            weekday_name_en = weekdays_en[weekday_index]
        except Exception:
            weekday_name_en = ''
        
        result = {
            "date": next_holiday_info['date'],
            "name": next_holiday_info['name'],
            "note": next_holiday_info.get('note', ''),
            "days_until": days_until,
            "weekday_name_en": weekday_name_en
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取下一个节假日失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'  

@mcp.tool()
async def current_year_work_days() -> str:
    """获取当前年份调休工作日安排
    
    Returns:
        包含当前年份调休工作日的JSON字符串
    """
    try:
        current_year = datetime.now().year
        holiday_data = await fetch_holiday_data(current_year)
        
        if not holiday_data:
            return '{"error": "无法获取节假日数据"}'
        
        work_days = []
        for day in holiday_data.get('days', []):
            if not day.get('isOffDay', True) and day.get('name'):  # 调休工作日
                # 获取星期几信息
                try:
                    date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
                    weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_index = date_obj.weekday()
                    weekday_name_en = weekdays_en[weekday_index]
                except Exception:
                    weekday_name_en = ''
                
                work_days.append({
                    "date": day['date'],
                    "name": day['name'],
                    "note": day.get('note', ''),
                    "weekday_name_en": weekday_name_en
                })
        
        result = {
            "year": current_year,
            "work_days": work_days,
            "total_count": len(work_days)
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取当前年份调休工作日失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'  

# 农历转换工具
@mcp.tool()
async def gregorian_to_lunar(year: int, month: int, day: int) -> str:
    """公历转农历
    
    Args:
        year: 公历年份
        month: 公历月份 (1-12)
        day: 公历日期 (1-31)
    
    Returns:
        包含农历信息的JSON字符串
    """
    try:
        # 这里应该导入农历转换模块，为了简化示例，返回基本信息
        from .data.bazi_calculator import BaziCalculator
        
        calculator = BaziCalculator()
        lunar_info = calculator.gregorian_to_lunar(year, month, day)
        
        import json
        return json.dumps(lunar_info, ensure_ascii=False, indent=2)
        
    except ImportError:
        # 如果模块不存在，返回简化版本
        result = {
            "gregorian_date": f"{year}-{month:02d}-{day:02d}",
            "lunar_year": year,
            "lunar_month": month,
            "lunar_day": day,
            "note": "农历转换功能需要完整的农历计算模块"
        }
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"公历转农历失败: {e}")
        return f'{{"error": "转换失败: {str(e)}"}}'  

@mcp.tool()
async def get_weekday(year: int, month: int, day: int) -> str:
    """获取指定日期是星期几
    
    Args:
        year: 年份
        month: 月份 (1-12)
        day: 日期 (1-31)
    
    Returns:
        包含星期几信息的JSON字符串
    """
    try:
        date_obj = datetime(year, month, day)
        weekdays_cn = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        weekday_index = date_obj.weekday()
        
        result = {
            "date": f"{year}-{month:02d}-{day:02d}",
            "weekday_index": weekday_index + 1,  # 1-7，周一为1
            "weekday_name_cn": weekdays_cn[weekday_index],
            "weekday_name_en": weekdays_en[weekday_index],
            "is_weekend": weekday_index >= 5
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取星期几失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'  

if __name__ == "__main__":
    mcp.run()