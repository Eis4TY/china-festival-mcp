# 使用示例

本文档提供了中国节假日MCP服务器的详细使用示例，帮助您快速上手并充分利用各项功能。

## 📋 目录

- [基础使用](#基础使用)
- [节假日查询](#节假日查询)
- [农历转换](#农历转换)
- [二十四节气](#二十四节气)
- [八字计算](#八字计算)
- [错误处理](#错误处理)

## 基础使用

### 启动服务器

```bash
# 进入项目目录
cd china-festival-mcp

# 激活虚拟环境
source venv/bin/activate

# 启动MCP服务器
python -m src.server
```

### 在Claude Desktop中使用

配置完成后，您可以直接在Claude Desktop中使用自然语言查询：

```
用户: 2024年春节是哪一天？
Claude: 我来为您查询2024年春节的日期...
```

## 节假日查询

### 查询法定节假日

```python
# 查询元旦
result = holiday_info("2024-01-01")
# 返回: {
#   "date": "2024-01-01",
#   "name": "元旦",
#   "type": "holiday",
#   "is_holiday": true,
#   "is_work_day": false,
#   "note": "法定节假日",
#   "weekday_name_en": "Monday"
# }

# 查询春节
result = holiday_info("2024-02-10")
# 返回: {
#   "date": "2024-02-10",
#   "name": "春节",
#   "type": "holiday",
#   "is_holiday": true,
#   "is_work_day": false,
#   "note": "法定节假日",
#   "weekday_name_en": "Saturday"
# }
```

### 查询调休日

```python
# 查询调休工作日
result = holiday_info("2024-02-04")
# 返回: {
#   "date": "2024-02-04",
#   "name": null,
#   "type": "workday",
#   "is_holiday": false,
#   "is_work_day": true,
#   "note": "调休工作日",
#   "weekday_name_en": "Sunday"
# }
```

### 实际对话示例

```
用户: 2024年国庆节放几天假？
Claude: 我来查询2024年国庆节的放假安排...

根据查询结果，2024年国庆节假期安排如下：
- 10月1日（Tuesday）：国庆节，法定节假日
- 10月2日（Wednesday）：国庆节假期
- 10月3日（Thursday）：国庆节假期
- 10月4日（Friday）：国庆节假期
- 10月5日（Saturday）：国庆节假期
- 10月6日（Sunday）：国庆节假期
- 10月7日（Monday）：国庆节假期

共放假7天，10月8日（Tuesday）正常上班。
```

## 农历转换

### 公历转农历

```python
# 查询2024年元旦对应的农历日期
result = gregorian_to_lunar("2024-01-01")
# 返回: {
#   "gregorian_date": "2024-01-01",
#   "lunar_year": 2023,
#   "lunar_month": 11,
#   "lunar_day": 20,
#   "is_leap_month": false,
#   "zodiac": "兔"
# }
```

### 农历转公历

```python
# 查询农历2024年正月初一对应的公历日期
result = lunar_to_gregorian(2024, 1, 1, false)
# 返回: {
#   "lunar_date": "2024年正月初一",
#   "gregorian_year": 2024,
#   "gregorian_month": 2,
#   "gregorian_day": 10,
#   "gregorian_date": "2024-02-10"
# }
```

### 获取详细农历信息

```python
# 获取详细的农历描述
result = get_lunar_string("2024-02-10")
# 返回: {
#   "gregorian_date": "2024-02-10",
#   "lunar_year": 2024,
#   "lunar_month": 1,
#   "lunar_day": 1,
#   "is_leap_month": false,
#   "zodiac": "龙",
#   "year_gan_zhi": "甲辰",
#   "tian_gan": "甲",
#   "di_zhi": "辰",
#   "lunar_month_name": "正月",
#   "lunar_day_name": "初一",
#   "lunar_string": "甲辰年 正月 初一"
# }
```

### 实际对话示例

```
用户: 我想知道2024年中秋节是农历几月几日？
Claude: 2024年中秋节是9月17日，让我查询对应的农历日期...

2024年9月17日（中秋节）对应的农历信息：
- 农历日期：甲辰年 八月 十五
- 生肖：龙年
- 干支：甲辰年
- 是否闰月：否

这正好是传统的农历八月十五中秋节。
```

## 二十四节气

### 查询月份节气

```python
# 查询2024年3月的节气
result = get_24_lunar_feast("2024-03-01")
# 返回: {
#   "year": 2024,
#   "month": 3,
#   "solar_terms": [
#     {
#       "name": "惊蛰",
#       "date": "2024-03-05",
#       "days_until": 4,
#       "season": "春季"
#     },
#     {
#       "name": "春分",
#       "date": "2024-03-20",
#       "days_until": 19,
#       "season": "春季"
#     }
#   ]
# }
```

### 实际对话示例

```
用户: 2024年夏至是哪一天？有什么特点？
Claude: 让我查询2024年夏至的具体信息...

2024年夏至是6月21日。夏至的特点：
- 日期：2024年6月21日
- 季节：夏季
- 特点：这是一年中白昼最长、黑夜最短的一天
- 意义：标志着夏季的正式开始，太阳直射北回归线
- 传统习俗：古代有祭祀天地的传统，现代人们注意防暑降温
```

## 八字计算

### 基础八字计算

```python
# 计算2024年1月1日中午12点的八字
result = get_8zi("2024-01-01", 12, 0)
# 返回详细的八字信息，包括四柱、五行等
```

### 不同时辰的八字

```python
# 子时（0点）
result = get_8zi("2024-01-01", 0, 0)

# 午时（12点）
result = get_8zi("2024-01-01", 12, 0)

# 酉时（18点）
result = get_8zi("2024-01-01", 18, 0)
```

### 实际对话示例

```
用户: 我想算一下1990年5月15日下午3点出生的人的八字
Claude: 我来为您计算1990年5月15日下午3点（15:00）的八字...

八字信息：
- 出生日期：1990年5月15日 15:00
- 年柱：庚午（金马）
- 月柱：辛巳（金蛇）
- 日柱：癸酉（水鸡）
- 时柱：己未（土羊）
- 完整八字：庚午 辛巳 癸酉 己未
- 生肖：马
- 五行分析：
  - 年：庚（金）午（火）
  - 月：辛（金）巳（火）
  - 日：癸（水）酉（金）
  - 时：己（土）未（土）
```

## 错误处理

### 日期格式错误

```python
# 错误的日期格式
result = holiday_info("2024/01/01")  # 应该使用 2024-01-01
# 返回错误信息：
# {
#   "error": "日期格式错误，应为YYYY-MM-DD格式",
#   "error_code": "VALIDATION_ERROR",
#   "details": {"field": "date", "value": "2024/01/01"}
# }
```

### 无效日期

```python
# 无效的日期
result = holiday_info("2024-02-30")  # 2月没有30日
# 返回错误信息
```

### 参数缺失

```python
# 缺少必要参数
result = lunar_to_gregorian()  # 缺少年月日参数
# 返回错误信息
```

## 星期几计算

### 基础星期几查询

```python
# 查询2024年1月1日是星期几
result = get_weekday(2024, 1, 1)
# 返回: {
#   "weekday_number": 1,
#   "weekday_name_zh": "星期一",
#   "weekday_name_en": "Monday",
#   "date": "2024-01-01"
# }
```

### 查询特殊日期

```python
# 查询闰年2月29日
result = get_weekday(2024, 2, 29)
# 返回: {
#   "weekday_number": 4,
#   "weekday_name_zh": "星期四",
#   "weekday_name_en": "Thursday",
#   "date": "2024-02-29"
# }

# 查询国庆节
result = get_weekday(2024, 10, 1)
# 返回: {
#   "weekday_number": 2,
#   "weekday_name_zh": "星期二",
#   "weekday_name_en": "Tuesday",
#   "date": "2024-10-01"
# }
```

### 实际对话示例

```
用户: 2024年春节是星期几？
Claude: 让我查询2024年春节（2月10日）是星期几...

2024年春节（2月10日）是星期六。
- 日期：2024-02-10
- 星期：星期六（Saturday）
- 星期数字：6

这意味着2024年春节假期从星期六开始，非常适合连休安排。
```

```
用户: 我想知道我的生日2024年8月15日是星期几？
Claude: 让我查询2024年8月15日是星期几...

您的生日2024年8月15日是星期四。
- 日期：2024-08-15
- 星期：星期四（Thursday）
- 星期数字：4

如果您想庆祝生日，可以考虑在周末（8月17-18日）安排聚会活动。
```

## 注意事项

1. **日期格式**：请始终使用 YYYY-MM-DD 格式
2. **时间范围**：支持1900-2100年的日期查询
3. **节假日数据**：基于官方发布的节假日安排
4. **星期几计算**：基于标准公历算法，支持历史和未来日期
