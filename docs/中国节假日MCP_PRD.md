

# 中国节假日MCP服务器

MCP 部署方式：Python 服务器，stdio 模式。

## 核心功能

### 节假日查询
- `holiday_info(date?)` - 查询指定日期节假日信息
- `current_year_holidays()` - 获取当前年份所有节假日
- `next_holiday()` - 查询下一个节假日以及距离当前日期的天数
- `is_holiday(date)` - 判断具体日期是否为节假日
- `current_year_work_days()` - 获取当前年份的调休工作日安排

### 农历转换
- `gregorian_to_lunar(year, month, day)` - 公历转农历
- `lunar_to_gregorian(lunar_year, lunar_month, lunar_day, is_leap_month?)` - 农历转公历。用于换算中国传统节日的阳历日期。如查询七夕节是几号，根据经验七夕节固定在农历七月初七，则传入农历日期获取公历日期。
- `get_lunar_string(lunar_year, lunar_month, lunar_day, is_leap_month?)` - 农历信息中文描述。返回对应的生肖、天干、地支、月份中文名、日期中文名

### 传统历法
- `get_24_lunar_feast(year, month, day)` - 节气与月建查询
- `get_8zi(year, month, day, hour, minute)` - 八字计算

## 技术要求

- **Python版本：** >= 3.8
- **数据源：** holiday-cn项目 + 内置农历算法
- **支持范围：** 1901-2100年
- **缓存：** 24小时内存缓存

## 部署方式

### 使用 uvx（推荐）
```bash
# 直接运行（无需安装）
uvx china-festival-mcp

# 或指定版本
uvx china-festival-mcp@latest
```

### 传统方式
```bash
# pip安装
pip install china-festival-mcp
python -m china_festival_mcp

# 开发模式
git clone <repo>
cd china-festival-mcp
pip install -e .
python -m china_festival_mcp
```

### MCP配置
在Claude Desktop配置文件中添加：
```json
{
  "mcpServers": {
    "china-festival": {
      "command": "uvx",
      "args": ["china-festival-mcp"]
    }
  }
}
```

