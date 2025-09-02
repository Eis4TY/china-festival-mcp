"""节假日查询工具模块"""

import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from mcp.types import Tool, TextContent
try:
    from src.utils.logger import get_logger, log_function_call
    from src.utils.error_handler import (
        handle_errors, validate_date_string, validate_year, validate_month, validate_day,
        create_error_response, MCPError, ValidationError
    )
    from src.utils.cache import cache_result
    from src.utils.performance import monitor_performance
    from src.utils.date_utils import get_weekday
except ImportError:
    # 如果导入失败，定义简单的替代函数
    def get_logger(name):
        import logging
        return logging.getLogger(name)
    
    def log_function_call(func_name, params, result=None, error=None):
        pass
    
    def handle_errors(return_on_error=None):
        def decorator(func):
            return func
        return decorator
    
    def validate_date_string(date_str):
        return True
    
    def validate_year(year):
        return int(year)
    
    def validate_month(month):
        return int(month)
    
    def validate_day(day):
        return int(day)
    
    def create_error_response(error):
        return {"error": str(error)}
    
    def cache_result(ttl=None, key_func=None, enabled=True):
        def decorator(func):
            return func
        return decorator
    
    def monitor_performance(include_system_metrics=False):
        def decorator(func):
            return func
        return decorator
    
    class MCPError(Exception):
        pass
    
    class ValidationError(Exception):
        pass

# 数据源配置
PRIMARY_DATA_SOURCE = "https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"
BACKUP_DATA_SOURCE = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json"


class HolidayTools:
    """节假日查询工具类"""
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """获取所有节假日相关工具"""
        return [
            Tool(
                name="holiday_info",
                description="查询指定日期的节假日信息，包含是否为节假日的判断",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "查询日期，格式：YYYY-MM-DD，不指定则查询当前日期"
                        }
                    }
                }
            ),
            Tool(
                name="current_year_holidays",
                description="获取当前年份所有法定节假日",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="next_holiday",
                description="获取距离当前日期最近的下一个节假日",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="current_year_work_days",
                description="获取当前年份调休工作日安排",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @staticmethod
    async def fetch_holiday_data(year: int) -> Optional[Dict[str, Any]]:
        """获取指定年份的节假日数据"""
        # 简单的内存缓存
        cache_key = f"holiday_data_{year}"
        
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
                        return data
                except Exception as e:
                    print(f"从{url}获取数据失败: {e}")
                    continue
        
        print(f"无法获取{year}年节假日数据")
        return None
    
    @staticmethod
    async def get_holiday_info(date_str: Optional[str] = None) -> Dict[str, Any]:
        """获取指定日期的节假日信息，包含是否为节假日的判断"""
        try:
            # 如果没有提供日期，使用当前日期
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 验证日期格式
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return {"error": "日期格式错误，请使用YYYY-MM-DD格式"}
            
            # 获取星期几信息
            try:
                weekday_info = get_weekday(date_obj.year, date_obj.month, date_obj.day)
                weekday_name_en = weekday_info.get('weekday_name_en', '')
            except Exception as e:
                weekday_name_en = ''
                print(f"获取星期几信息失败: {e}")
            
            year = int(date_str.split('-')[0])
            holiday_data = await HolidayTools.fetch_holiday_data(year)
            
            if not holiday_data:
                return {"error": "无法获取节假日数据"}
            
            # 查找指定日期的信息
            date_info = None
            for day in holiday_data.get('days', []):
                if day.get('date') == date_str:
                    date_info = day
                    break
            
            if date_info:
                is_holiday = date_info.get('isOffDay', False)
                holiday_name = date_info.get('name', '')
                
                return {
                    "date": date_str,
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
                return {
                    "date": date_str,
                    "name": "普通日",
                    "type": "normal",
                    "is_holiday": is_weekend,
                    "is_work_day": not is_weekend,
                    "note": "周末" if is_weekend else "工作日",
                    "weekday_name_en": weekday_name_en
                }
        except Exception as e:
            print(f"查询节假日信息失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    @staticmethod
    async def get_current_year_holidays() -> Dict[str, Any]:
        """获取当前年份所有节假日"""
        try:
            year = datetime.now().year
            holiday_data = await HolidayTools.fetch_holiday_data(year)
            
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
            print(f"查询当前年份节假日失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    @staticmethod
    async def get_next_holiday() -> Dict[str, Any]:
        """获取下一个节假日"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_year = datetime.now().year
            
            # 获取当前年份和下一年的节假日数据
            holiday_data = await HolidayTools.fetch_holiday_data(current_year)
            next_year_data = await HolidayTools.fetch_holiday_data(current_year + 1)
            
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
                
                # 获取星期几信息
                try:
                    weekday_info = get_weekday(holiday_date.year, holiday_date.month, holiday_date.day)
                    weekday_name_en = weekday_info.get('weekday_name_en', '')
                except Exception as e:
                    weekday_name_en = ''
                    print(f"获取星期几信息失败: {e}")
                
                return {
                    "name": next_holiday.get('name', ''),
                    "date": next_holiday.get('date'),
                    "days_until": days_until,
                    "note": next_holiday.get('note', ''),
                    "weekday_name_en": weekday_name_en
                }
            else:
                return {"error": "未找到未来的节假日"}
        except Exception as e:
            print(f"查询下一个节假日失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    

    
    @staticmethod
    async def get_current_year_work_days() -> Dict[str, Any]:
        """获取当前年份调休工作日安排"""
        try:
            year = datetime.now().year
            holiday_data = await HolidayTools.fetch_holiday_data(year)
            
            if not holiday_data:
                return {"error": "无法获取节假日数据"}
            
            # 提取所有调休工作日
            work_days = []
            for day in holiday_data.get('days', []):
                if not day.get('isOffDay', False) and day.get('name'):  # 调休工作日
                    work_days.append({
                        "date": day.get('date'),
                        "name": day.get('name', '') + "补班",
                        "note": day.get('note', '')
                    })
            
            return {
                "year": year,
                "work_days": work_days,
                "total_count": len(work_days)
            }
        except Exception as e:
            print(f"查询调休工作日失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    @staticmethod
    async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """处理工具调用"""
        try:
            if name == "holiday_info":
                result = await HolidayTools.get_holiday_info(arguments.get("date"))
            elif name == "current_year_holidays":
                result = await HolidayTools.get_current_year_holidays()
            elif name == "next_holiday":
                result = await HolidayTools.get_next_holiday()
            elif name == "current_year_work_days":
                result = await HolidayTools.get_current_year_work_days()
            else:
                result = {"error": f"未知的工具: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            print(f"处理工具调用失败: {e}")
            error_result = {"error": f"工具调用失败: {str(e)}"}
            return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]