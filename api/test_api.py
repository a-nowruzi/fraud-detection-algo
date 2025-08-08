#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فایل تست برای API تشخیص تقلب پزشکی
"""

import requests
import json
import time
import base64
from datetime import datetime

# تنظیمات API
BASE_URL = "http://localhost:5000"

def test_health_check():
    """تست بررسی سلامت سیستم"""
    print("🔍 تست بررسی سلامت سیستم...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ سیستم سالم است")
            print(f"   - وضعیت: {data['status']}")
            print(f"   - مدل بارگذاری شده: {data['model_loaded']}")
            print(f"   - داده‌ها بارگذاری شده: {data['data_loaded']}")
            print(f"   - زمان: {data['timestamp']}")
            return True
        else:
            print(f"❌ خطا در بررسی سلامت: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در اتصال به API: {e}")
        return False

def test_stats():
    """تست دریافت آمار سیستم"""
    print("\n📊 تست دریافت آمار سیستم...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ آمار سیستم دریافت شد")
            print(f"   - کل نسخه‌ها: {data['total_prescriptions']:,}")
            print(f"   - نسخه‌های تقلبی: {data['fraud_prescriptions']:,}")
            print(f"   - نسخه‌های نرمال: {data['normal_prescriptions']:,}")
            print(f"   - درصد تقلب: {data['fraud_percentage']}%")
            print(f"   - تعداد ویژگی‌ها: {data['features_count']}")
            return True
        else:
            print(f"❌ خطا در دریافت آمار: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در دریافت آمار: {e}")
        return False

def test_prediction():
    """تست تشخیص تقلب"""
    print("\n🔮 تست تشخیص تقلب...")
    
    # داده‌های تست
    test_data = {
        "ID": 48928,
        "jalali_date": "1361/05/04",
        "Adm_date": "1403/08/05",
        "Service": "ویزیت متخصص",
        "provider_name": "حسینخان خسروخاور",
        "provider_specialty": "دکترای حرفه‌ای پزشکی",
        "cost_amount": 2000000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ تشخیص تقلب انجام شد")
            print(f"   - پیش‌بینی: {data['prediction']}")
            print(f"   - امتیاز: {data['score']:.3f}")
            print(f"   - تقلب: {'بله' if data['is_fraud'] else 'خیر'}")
            print(f"   - تعداد شاخص‌های ریسک: {len(data['risk_scores'])}")
            
            # نمایش شاخص‌های ریسک
            risk_names = [
                "نسبت پزشکان", "نسبت بیماران", "تغییر هزینه پزشک",
                "تغییر هزینه بیمار", "اختلاف خدمت", "تغییر خدمت پزشک",
                "تغییر تخصص پزشک", "تغییر مستقیم تخصص", "تغییر خدمت بیمار",
                "تغییر کلی خدمت", "نسبت خدمات"
            ]
            
            print("\n📈 شاخص‌های ریسک:")
            for i, (name, score) in enumerate(zip(risk_names, data['risk_scores'])):
                print(f"   {i+1:2d}. {name}: {score:.2f}")
            
            return True
        else:
            print(f"❌ خطا در تشخیص تقلب: {response.status_code}")
            print(f"   پاسخ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطا در تشخیص تقلب: {e}")
        return False

def test_charts():
    """تست نمودارها"""
    print("\n📊 تست نمودارها...")
    
    # تست نمودار تقلب بر اساس استان
    try:
        response = requests.get(f"{BASE_URL}/charts/fraud-by-province")
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']:
                print("✅ نمودار تقلب بر اساس استان ایجاد شد")
            else:
                print("❌ نمودار تقلب بر اساس استان ایجاد نشد")
        else:
            print(f"❌ خطا در نمودار استان: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در نمودار استان: {e}")
    
    # تست نمودار تقلب بر اساس جنسیت
    try:
        response = requests.get(f"{BASE_URL}/charts/fraud-by-gender")
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']:
                print("✅ نمودار تقلب بر اساس جنسیت ایجاد شد")
            else:
                print("❌ نمودار تقلب بر اساس جنسیت ایجاد نشد")
        else:
            print(f"❌ خطا در نمودار جنسیت: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در نمودار جنسیت: {e}")
    
    # تست نمودار تقلب بر اساس سن
    try:
        response = requests.get(f"{BASE_URL}/charts/fraud-by-age")
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']:
                print("✅ نمودار تقلب بر اساس سن ایجاد شد")
            else:
                print("❌ نمودار تقلب بر اساس سن ایجاد نشد")
        else:
            print(f"❌ خطا در نمودار سن: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در نمودار سن: {e}")

def test_risk_indicators_chart():
    """تست نمودار شاخص‌های ریسک"""
    print("\n📈 تست نمودار شاخص‌های ریسک...")
    
    test_data = {
        "ID": 48928,
        "jalali_date": "1361/05/04",
        "Adm_date": "1403/08/05",
        "Service": "ویزیت متخصص",
        "provider_name": "حسینخان خسروخاور",
        "provider_specialty": "دکترای حرفه‌ای پزشکی",
        "cost_amount": 2000000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/charts/risk-indicators", json=test_data)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']:
                print("✅ نمودار شاخص‌های ریسک ایجاد شد")
                print(f"   - پیش‌بینی: {data['prediction']['prediction']}")
                print(f"   - تقلب: {'بله' if data['prediction']['is_fraud'] else 'خیر'}")
            else:
                print("❌ نمودار شاخص‌های ریسک ایجاد نشد")
        else:
            print(f"❌ خطا در نمودار شاخص‌های ریسک: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در نمودار شاخص‌های ریسک: {e}")

def test_invalid_data():
    """تست داده‌های نامعتبر"""
    print("\n⚠️ تست داده‌های نامعتبر...")
    
    # تست با فیلدهای ناقص
    invalid_data = {
        "ID": 48928,
        "jalali_date": "1361/05/04"
        # فیلدهای دیگر حذف شده‌اند
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=invalid_data)
        if response.status_code == 400:
            data = response.json()
            print(f"✅ خطای اعتبارسنجی به درستی مدیریت شد")
            print(f"   - پیام خطا: {data.get('error', 'خطای نامشخص')}")
            return True
        else:
            print(f"❌ خطای اعتبارسنجی مدیریت نشد: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در تست داده‌های نامعتبر: {e}")
        return False

def main():
    """تابع اصلی تست"""
    print("🚀 شروع تست API تشخیص تقلب پزشکی")
    print("=" * 50)
    
    # انتظار برای آماده شدن API
    print("⏳ منتظر آماده شدن API...")
    time.sleep(5)
    
    # اجرای تست‌ها
    tests = [
        ("بررسی سلامت سیستم", test_health_check),
        ("دریافت آمار سیستم", test_stats),
        ("تشخیص تقلب", test_prediction),
        ("نمودارها", test_charts),
        ("نمودار شاخص‌های ریسک", test_risk_indicators_chart),
        ("داده‌های نامعتبر", test_invalid_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ خطای غیرمنتظره در {test_name}: {e}")
            results.append((test_name, False))
    
    # خلاصه نتایج
    print("\n" + "="*50)
    print("📋 خلاصه نتایج تست:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 نتیجه کلی: {passed}/{total} تست موفق")
    
    if passed == total:
        print("🎉 تمام تست‌ها با موفقیت انجام شدند!")
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند. لطفاً مشکلات را بررسی کنید.")

if __name__ == "__main__":
    main()
