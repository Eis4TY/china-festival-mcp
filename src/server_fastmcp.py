import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

# 导入工具函数
try:
    from utils.logger import setup_logger
    from utils.date_utils import get_weekday
    from tools.lunar import LunarTools
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)
    
    def get_weekday(year, month, day):
        date_obj = datetime(year, month, day)
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {'weekday_name_en': weekdays[date_obj.weekday()]}
    
    # 如果导入失败，创建一个简化的LunarTools类
    class LunarTools:
        @staticmethod
        def lunar_to_gregorian(year, month, day, is_leap=False):
            return {"error": "农历转换模块未安装"}
        
        @staticmethod
        def get_lunar_string(year, month, day):
            return {"error": "农历转换模块未安装"}
        
        @staticmethod
        def get_24_lunar_feast(year, month):
            return {"error": "农历转换模块未安装"}
        
        @staticmethod
        def get_8zi(year, month, day, hour=12):
            return {"error": "农历转换模块未安装"}

# 设置日志
logger = setup_logger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("中国节假日MCP服务器")

# 数据源配置
PRIMARY_DATA_SOURCE = "https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"
BACKUP_DATA_SOURCE = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json"

# TTL 缓存配置 (7天)
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60

# 简单的内存缓存
_holiday_cache: Dict[int, Dict[str, Any]] = {}
_holiday_cache_ts: Dict[int, float] = {}  # 缓存时间戳
_refreshing_years: set = set()  # 正在刷新的年份

async def fetch_holiday_data(year: int) -> Optional[Dict[str, Any]]:
    """获取指定年份的节假日数据，支持 TTL 缓存和后台刷新"""
    import time
    
    current_time = time.time()
    
    # 检查缓存是否存在且未过期
    if year in _holiday_cache:
        cache_time = _holiday_cache_ts.get(year, 0)
        if current_time - cache_time < CACHE_TTL_SECONDS:
            # 缓存未过期，直接返回
            return _holiday_cache[year]
        else:
            # 缓存过期，触发后台刷新（如果尚未在刷新中）
            if year not in _refreshing_years:
                _refreshing_years.add(year)
                # 启动后台刷新任务
                asyncio.create_task(_refresh_holiday_data(year))
            # 返回过期的缓存数据（stale-while-revalidate）
            return _holiday_cache[year]
    
    # 缓存不存在，同步获取数据
    data = await _fetch_holiday_data_sync(year)
    if data:
        _holiday_cache[year] = data
        _holiday_cache_ts[year] = current_time
    
    return data


async def _fetch_holiday_data_sync(year: int) -> Optional[Dict[str, Any]]:
    """同步获取节假日数据的内部函数"""
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
                logger.warning(f"从{url}获取数据失败: {e}")
                continue
    
    logger.error(f"无法获取{year}年节假日数据")
    return None


async def _refresh_holiday_data(year: int):
    """后台刷新指定年份的节假日数据"""
    import time
    
    try:
        # 获取新数据
        new_data = await _fetch_holiday_data_sync(year)
        if new_data:
            # 更新缓存和时间戳
            _holiday_cache[year] = new_data
            _holiday_cache_ts[year] = time.time()
            logger.info(f"后台刷新{year}年节假日数据成功")
        else:
            logger.warning(f"后台刷新{year}年节假日数据失败")
    except Exception as e:
        logger.error(f"后台刷新{year}年节假日数据异常: {e}")
    finally:
        # 移除刷新中标记
        _refreshing_years.discard(year)

@mcp.tool()
async def holiday_info(date: str = None) -> str:
    """查询指定日期的节假日信息，包含是否为节假日的判断
    date: 查询日期，格式：YYYY-MM-DD，不指定则查询当前日期
    """
    try:
        # 如果没有提供日期，默认使用当前日期
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
                "name": " ",
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
async def next_holiday(date: str = None) -> str:
    """获取距离指定日期最近的下一个节假日
    date: 起始日期，格式：YYYY-MM-DD，不指定则使用当前日期
    """
    try:
        # 如果没有提供日期，默认使用当前日期
        if not date:
            today = datetime.now().date()
        else:
            # 验证日期格式
            try:
                today = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        current_year = today.year
        
        # 先查找当前年份的节假日
        holiday_data = await fetch_holiday_data(current_year)
        
        next_holiday_info = None
        
        # 查找当前年份的下一个节假日
        if holiday_data:
            for day in holiday_data.get('days', []):
                if day.get('isOffDay', False) and day.get('name'):
                    holiday_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
                    if holiday_date > today:
                        next_holiday_info = day
                        break
        
        # 如果当前年份没有找到，查找下一年的第一个节假日；若数据库未更新则兜底为次年元旦
        if not next_holiday_info:
            next_year = current_year + 1
            next_year_data = await fetch_holiday_data(next_year)
            if next_year_data:
                for day in next_year_data.get('days', []):
                    if day.get('isOffDay', False) and day.get('name'):
                        next_holiday_info = day
                        break
        
        # 数据库未更新，则使用次年元旦作为兜底
        if not next_holiday_info:
                new_year_date_obj = datetime(next_year, 1, 1).date()
                next_holiday_info = {
                    "date": new_year_date_obj.strftime("%Y-%m-%d"),
                    "name": "元旦",
                    "note": ""
                }
        
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
    """获取当前年份所有因调休导致需要上班上课的原休息日
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
                    "name": day['name'] + "-需要上班",
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

# 农历转换工具类
class LunarTools:
    """农历转换工具类"""
    
    # 农历数据
    LUNAR_DATA = (
        1198, 2647, 330317, 3366, 3477, 265557, 1386, 2477, 18781, 1198,
        398491, 2637, 3365, 334501, 2900, 3434, 133485, 2395, 461111, 1175,
        2635, 333387, 1701, 1748, 267701, 694, 2391, 133423, 1175, 396438,
        3402, 3749, 331177, 1453, 694, 201326, 2350, 465197, 3221, 3402,
        400202, 2901, 1386, 267611, 605, 2349, 137515, 2709, 464533, 1738,
        2901, 330421, 1242, 2651, 199255, 1323, 529706, 3733, 1706, 398762,
        2741, 1206, 267438, 2647, 1318, 204070, 3477, 461653, 1386, 2413,
        330077, 1197, 2637, 268877, 3365, 531109, 2900, 2922, 398042, 2395,
        1179, 267415, 2635, 661067, 1701, 1748, 398772, 2742, 2391, 330031,
        1175, 1611, 200010, 3749, 527717, 1452, 2742, 332397, 2350, 3222,
        268949, 3402, 3493, 133973, 1386, 464219, 605, 2349, 334123, 2709,
        2890, 267946, 2773, 592565, 1210, 2651, 395863, 1323, 2707, 265877,
        1706, 2773, 18869, 1206, 51799, 2638, 3366, 44691, 3411, 1450,
        26293, 2413, 92509, 1197, 2637, 55883, 3365, 3410, 44458, 2906,
        1389, 18779, 1179, 62615, 2635, 2725, 46757, 1746, 2778, 27319
    )
    
    # 天干地支
    TIAN_GAN = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
    DI_ZHI = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
    
    # 生肖
    ZODIAC = ("鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪")
    
    # 农历日期名
    LUNAR_DAY_NAMES = (
        "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
        "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
        "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
    )
    
    # 农历月份名
    LUNAR_MONTH_NAMES = (
        "", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "腊"
    )
    
    @staticmethod
    def gregorian_to_lunar(year, month, day):
        """公历转农历"""
        try:
            # 公历每月前面的天数
            month_add = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
            
            # 计算到初始时间1901年2月19日的天数：1921-2-19(正月初一)
            the_date = (year - 1901) * 365 + (year - 1901) // 4 + day + month_add[month - 1] - 38 - 11
            
            if the_date <= 0:
                return None, None, None, False
            
            # 闰年处理
            if (year % 4 == 0) and (month > 2):
                the_date += 1
            
            # 计算农历天干、地支、月、日
            is_end = False
            m = 0
            
            while not is_end:
                if LunarTools.LUNAR_DATA[m] < 4095:
                    k = 11
                else:
                    k = 12
                
                n = k
                while n >= 0:
                    bit = LunarTools.LUNAR_DATA[m]
                    for i in range(1, n + 1):
                        bit = bit // 2
                    bit = bit % 2
                    
                    if the_date <= (29 + bit):
                        is_end = True
                        break
                    
                    the_date = the_date - 29 - bit
                    n = n - 1
                
                if is_end:
                    break
                m = m + 1
            
            cur_year = 1901 + m
            cur_month = k - n + 1
            cur_day = the_date
            
            if cur_day < 0:
                return None, None, None, False
            
            # 处理闰月
            embolism = False
            if k == 12:
                if cur_month == LunarTools.LUNAR_DATA[m] // 65536 + 1:
                    cur_month = 1 - cur_month
                elif cur_month > LunarTools.LUNAR_DATA[m] // 65536 + 1:
                    cur_month = cur_month - 1
            
            if cur_month < 1:
                lunar_month = -cur_month
                embolism = True
            else:
                lunar_month = cur_month
                embolism = False
            
            return cur_year, lunar_month, cur_day, embolism
            
        except Exception as e:
            logger.error(f"公历转农历失败: {e}")
            return None, None, None, False
    
    @staticmethod
    def lunar_to_gregorian(lunar_year, lunar_month, lunar_day, is_leap=False):
        """农历转公历"""
        try:
            # 从农历年份开始，逐日查找对应的公历日期
            start_date = datetime(lunar_year, 1, 1)
            
            for i in range(400):  # 最多查找400天
                test_date = start_date + timedelta(days=i)
                lunar_result = LunarTools.gregorian_to_lunar(test_date.year, test_date.month, test_date.day)
                
                if (lunar_result[0] == lunar_year and 
                    lunar_result[1] == lunar_month and 
                    lunar_result[2] == lunar_day and 
                    lunar_result[3] == is_leap):
                    return test_date.year, test_date.month, test_date.day
            
            return None, None, None
            
        except Exception as e:
            logger.error(f"农历转公历失败: {e}")
            return None, None, None
    
    @staticmethod
    def get_lunar_string(year, month, day):
        """获取农历日期的中文描述"""
        try:
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            lunar_result = LunarTools.gregorian_to_lunar(year, month, day)
            
            if lunar_result[0] is None:
                return {"error": "无法转换为农历"}
            
            lunar_year, lunar_month, lunar_day, is_leap = lunar_result
            
            # 生成属相
            zodiac_index = ((lunar_year - 4) % 60) % 12
            zodiac = LunarTools.ZODIAC[zodiac_index]
            
            # 生成天干地支
            tian_gan_index = ((lunar_year - 4) % 60) % 10
            di_zhi_index = ((lunar_year - 4) % 60) % 12
            tian_gan = LunarTools.TIAN_GAN[tian_gan_index]
            di_zhi = LunarTools.DI_ZHI[di_zhi_index]
            
            # 生成农历月份
            lunar_month_name = LunarTools.LUNAR_MONTH_NAMES[lunar_month] + "月"
            if is_leap:
                lunar_month_name = "闰" + lunar_month_name
            
            # 生成农历日期
            lunar_day_name = LunarTools.LUNAR_DAY_NAMES[lunar_day]
            
            return {
                "gregorian_date": date_str,
                "lunar_year": lunar_year,
                "lunar_month": lunar_month,
                "lunar_day": lunar_day,
                "is_leap_month": is_leap,
                "zodiac": zodiac,
                "year_gan_zhi": tian_gan + di_zhi,
                "tian_gan": tian_gan,
                "di_zhi": di_zhi,
                "lunar_month_name": lunar_month_name,
                "lunar_day_name": lunar_day_name,
                "lunar_string": f"{tian_gan}{di_zhi}年 {lunar_month_name} {lunar_day_name}"
            }
            
        except Exception as e:
            logger.error(f"获取农历字符串失败: {e}")
            return {"error": f"转换失败: {str(e)}"}

# 农历转换工具
@mcp.tool()
async def gregorian_to_lunar(date: str) -> str:
    """公历转农历
    date: 公历日期，格式：YYYY-MM-DD
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        year, month, day = date_obj.year, date_obj.month, date_obj.day
        lunar_result = LunarTools.gregorian_to_lunar(year, month, day)
        
        if lunar_result[0] is None:
            return '{"error": "无法转换为农历"}'
        
        lunar_year, lunar_month, lunar_day, is_leap = lunar_result
        
        # 生成属相
        zodiac_index = ((lunar_year - 4) % 60) % 12
        zodiac = LunarTools.ZODIAC[zodiac_index]
        
        result = {
            "gregorian_date": date,
            "lunar_year": lunar_year,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "is_leap_month": is_leap,
            "zodiac": zodiac
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"公历转农历失败: {e}")
        return f'{{"error": "转换失败: {str(e)}"}}'

@mcp.tool()
async def lunar_to_gregorian(date: str, is_leap: bool = False) -> str:
    """农历转公历。用于换算中国传统节日的阳历日期。如查询七夕节是几号，根据经验七夕节固定在农历七月初七，则传入农历日期获取公历日期。
    date: 农历日期，格式：YYYY-MM-DD
    is_leap: 是否为闰月，默认为False
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        year, month, day = date_obj.year, date_obj.month, date_obj.day
        gregorian_result = LunarTools.lunar_to_gregorian(year, month, day, is_leap)
        
        if gregorian_result[0] is None:
            return '{"error": "无法转换为公历"}'
        
        greg_year, greg_month, greg_day = gregorian_result
        
        result = {
            "lunar_date": f"{year}年{LunarTools.LUNAR_MONTH_NAMES[month]}月{LunarTools.LUNAR_DAY_NAMES[day]}",
            "gregorian_year": greg_year,
            "gregorian_month": greg_month,
            "gregorian_day": greg_day,
            "gregorian_date": f"{greg_year:04d}-{greg_month:02d}-{greg_day:02d}"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"农历转公历失败: {e}")
        return f'{{"error": "转换失败: {str(e)}"}}'

@mcp.tool()
async def get_lunar_string(date: str) -> str:
    """获取农历日期的生肖/干支纪年
    date: 公历日期，格式：YYYY-MM-DD
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        year, month, day = date_obj.year, date_obj.month, date_obj.day
        result = LunarTools.get_lunar_string(year, month, day)
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取农历信息失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'

@mcp.tool()
async def get_24_lunar_feast(date: str) -> str:
    """获取当月的二十四节气信息
    date: 日期，格式：YYYY-MM-DD
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        year, month = date_obj.year, date_obj.month
        
        # 导入节气模块
        try:
            from .data.solar_terms import get_solar_terms_for_month, get_season_by_solar_term
        except ImportError:
            try:
                from data.solar_terms import get_solar_terms_for_month, get_season_by_solar_term
            except ImportError:
                return '{"error": "节气模块未找到"}'
        
        # 获取该月份的所有节气
        month_terms = get_solar_terms_for_month(year, month)
        
        # 获取当前日期用于计算倒计时
        current_date = datetime.now().date()
        
        solar_terms_list = []
        for term_name, term_day in month_terms:
            term_date = f"{year:04d}-{month:02d}-{term_day:02d}"
            season = get_season_by_solar_term(term_name)
            
            # 计算距离该节气的天数
            term_date_obj = datetime(year, month, term_day).date()
            days_until = (term_date_obj - current_date).days
            
            solar_terms_list.append({
                "name": term_name,
                "date": term_date,
                "days_until": days_until,
                "season": season
            })
        
        result = {
            "year": year,
            "month": month,
            "solar_terms": solar_terms_list
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取节气信息失败: {e}")
        return f'{{"error": "查询失败: {str(e)}"}}'

@mcp.tool()
async def get_8zi(date: str, hour: int = 12, minute: int = 0) -> str:
    """计算八字（四柱）
    date: 日期，格式：YYYY-MM-DD
    hour: 小时 (0-23)，默认为12
    minute: 分钟 (0-59)，默认为0
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        # 验证时间参数
        if not (0 <= hour <= 23):
            return '{"error": "小时必须在0-23之间"}'
        if not (0 <= minute <= 59):
            return '{"error": "分钟必须在0-59之间"}'
        
        year, month, day = date_obj.year, date_obj.month, date_obj.day
        
        # 导入八字计算模块
        try:
            from .data.bazi_calculator import calculate_bazi
        except ImportError:
            try:
                from data.bazi_calculator import calculate_bazi
            except ImportError:
                return '{"error": "八字计算模块未找到"}'
        
        # 使用八字计算模块
        bazi_result = calculate_bazi(year, month, day, hour)
        
        # 只返回八字字符串
        result = {
            "eight_characters": bazi_result["eight_characters"]
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"计算八字失败: {e}")
        return f'{{"error": "计算失败: {str(e)}"}}'

@mcp.tool()
async def get_weekday(date: str) -> str:
    """获取指定日期是星期几
    date: 日期，格式：YYYY-MM-DD
    """
    try:
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return '{"error": "日期格式错误，请使用YYYY-MM-DD格式"}'
        
        weekdays_cn = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        weekday_index = date_obj.weekday()
        
        result = {
            "date": date,
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

def main():
    """主入口函数"""
    mcp.run()

if __name__ == "__main__":
    main()