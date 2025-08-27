#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试节气计算功能
"""

from datetime import datetime
from src.data.solar_terms import (
    get_solar_term_for_date,
    get_solar_terms_for_month,
    get_next_solar_term,
    get_season_by_solar_term,
    get_solar_term_date,
    get_all_solar_terms_for_year,
    SOLAR_TERMS
)

def test_solar_term_accuracy():
    """测试节气计算的准确性"""
    print("=== 测试节气计算准确性 ===")
    
    # 测试2024年的一些已知节气日期
    test_cases = [
        (2024, "立春", 2, 4),
        (2024, "春分", 3, 20),
        (2024, "夏至", 6, 21),
        (2024, "秋分", 9, 22),
        (2024, "冬至", 12, 21),
    ]
    
    for year, term, expected_month, expected_day in test_cases:
        actual_date = get_solar_term_date(year, term)
        if actual_date:
            print(f"{year}年{term}: 计算日期 {actual_date.month}月{actual_date.day}日, 预期 {expected_month}月{expected_day}日")
            if actual_date.month == expected_month and abs(actual_date.day - expected_day) <= 1:
                print("✓ 准确")
            else:
                print("✗ 不准确")
        else:
            print(f"✗ 无法计算{year}年{term}")
        print()

def test_get_solar_term_for_date():
    """测试根据日期获取节气"""
    print("=== 测试根据日期获取节气 ===")
    
    test_dates = [
        (2024, 2, 4),   # 立春
        (2024, 3, 20),  # 春分
        (2024, 6, 21),  # 夏至
        (2024, 9, 22),  # 秋分
        (2024, 12, 21), # 冬至
    ]
    
    for year, month, day in test_dates:
        term = get_solar_term_for_date(year, month, day)
        print(f"{year}年{month}月{day}日: {term if term else '非节气日'}")
    print()

def test_get_solar_terms_for_month():
    """测试获取月份节气"""
    print("=== 测试获取月份节气 ===")
    
    for month in [2, 6, 9, 12]:  # 测试几个月份
        terms = get_solar_terms_for_month(2024, month)
        print(f"2024年{month}月的节气:")
        for term, day in terms:
            print(f"  {term}: {day}日")
        print()

def test_get_next_solar_term():
    """测试获取下一个节气"""
    print("=== 测试获取下一个节气 ===")
    
    test_dates = [
        (2024, 1, 1),   # 年初
        (2024, 6, 15),  # 年中
        (2024, 12, 25), # 年末
    ]
    
    for year, month, day in test_dates:
        next_term = get_next_solar_term(year, month, day)
        if next_term:
            term, date = next_term
            print(f"{year}年{month}月{day}日之后的下一个节气: {term} ({date.strftime('%Y年%m月%d日')})")
        else:
            print(f"{year}年{month}月{day}日之后无下一个节气")
    print()

def test_get_season_by_solar_term():
    """测试根据节气获取季节"""
    print("=== 测试根据节气获取季节 ===")
    
    test_terms = ["立春", "立夏", "立秋", "立冬", "春分", "夏至", "秋分", "冬至"]
    
    for term in test_terms:
        season = get_season_by_solar_term(term)
        print(f"{term}: {season}")
    print()

def test_get_all_solar_terms_for_year():
    """测试获取全年节气"""
    print("=== 测试获取2024年全年节气 ===")
    
    terms = get_all_solar_terms_for_year(2024)
    
    print(f"2024年共有{len(terms)}个节气:")
    for i, (term, date) in enumerate(terms, 1):
        print(f"{i:2d}. {term}: {date.strftime('%m月%d日')}")
    print()

def test_year_range():
    """测试年份范围"""
    print("=== 测试年份范围 ===")
    
    # 测试边界年份
    test_years = [1900, 1901, 2024, 2050, 2051]
    
    for year in test_years:
        terms = get_all_solar_terms_for_year(year)
        if terms:
            print(f"{year}年: 支持 (共{len(terms)}个节气)")
        else:
            print(f"{year}年: 不支持")
    print()

if __name__ == "__main__":
    print("开始测试节气计算功能...\n")
    
    test_solar_term_accuracy()
    test_get_solar_term_for_date()
    test_get_solar_terms_for_month()
    test_get_next_solar_term()
    test_get_season_by_solar_term()
    test_get_all_solar_terms_for_year()
    test_year_range()
    
    print("测试完成!")