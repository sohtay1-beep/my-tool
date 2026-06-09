import os
import subprocess
import platform
import concurrent.futures
import ipaddress

def ping_ip(ip, timeout_ms):
    ip_str = str(ip)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = str(timeout_ms) if platform.system().lower() == 'windows' else str(timeout_ms / 1000)
    
    command = ['ping', param, '1', timeout_param, timeout_val, ip_str]
    
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        if output.returncode == 0:
            for line in output.stdout.split('\n'):
                if "time=" in line or "time<" in line:
                    parts = line.split("time")
                    time_part = parts[1].replace("=", "").replace("<", "").strip().split("ms")[0]
                    ping_time = float(time_part)
                    return ip_str, ping_time
    except Exception:
        pass
    return ip_str, None

def main():
    print("="*50)
    print("📡 اسکنر هوشمند و تعاملی رنج آی‌پي")
    print("="*50)
    
    # ۱. دریافت رنج‌های آی‌پی از کاربر
    print("\n🔹 رنج‌های آی‌پی (CIDR) مورد نظرت را وارد کن.")
    print("💡 نکته: می‌توانی چند رنج را با «کاما ,» یا «فاصله» از هم جدا کنی.")
    raw_ranges = input("✍️ رنج‌ها: ")
    
    # تمیزکاری ورودی کاربر و تبدیل به لیست
    processed_ranges = raw_ranges.replace(",", " ").split()
    
    if not processed_ranges:
        print("❌ هیچ رنجی وارد نشد. برنامه بسته می‌شود.")
        return

    # ۲. تنظیم سرعت (تعداد تردها)
    print("\n🔹 سرعت اسکن (تعداد درخواست‌های همزمان) را مشخص کن.")
    print("💡 پیشنهاد: برای گوشی و اینترنت معمولی 50، برای اینترنت قوی 100")
    try:
        max_threads = input("✍️ تعداد تسک همزمان [پیش‌فرض 50]: ")
        max_threads = int(max_threads) if max_threads.strip() else 50
    except ValueError:
        print("⚠️ ورودی نامعتبر بود. سرعت روی 50 تنظیم شد.")
        max_threads = 50

    # ۳. تنظیم حداکثر زمان انتظار (Timeout)
    print("\n🔹 حداکثر زمان انتظار برای پاسخ هر آی‌پی (به میلی‌ثانیه)؟")
    print("💡 پیشنهاد: 1000 یا 1500 (آی‌پی‌های با پینگ بالاتر از این حذف می‌شوند)")
    try:
        timeout_ms = input("✍️ تایم‌اوت [پیش‌فرض 1500]: ")
        timeout_ms = int(timeout_ms) if timeout_ms.strip() else 1500
    except ValueError:
        print("⚠️ ورودی نامعتبر بود. تایم‌اوت روی 1500 تنظیم شد.")
        timeout_ms = 1500

    # استخراج آی‌پی‌ها
    print("\n⏳ در حال پردازش و استخراج آی‌پی‌ها...")
    all_ips = []
    for r in processed_ranges:
        try:
            network = ipaddress.ip_network(r.strip(), strict=False)
            all_ips.extend(list(network.hosts()))
        except ValueError:
            print(f"⚠️ رنج نامعتبر سکیپ شد: {r}")
            
    total_ips = len(all_ips)
    if total_ips == 0:
        print("❌ هیچ آی‌پی معتبری برای اسکن یافت نشد!")
        return
        
    print(f"🔍 تعداد کل آی‌پی‌های استخراج شده: {total_ips}")
    print(f"⚡ شروع اسکن با {max_threads} رشته همزمان... لطفا منتظر بمانید.\n")
    
    healthy_ips = []
    
    # اجرای همزمان پینگ‌ها
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(lambda ip: ping_ip(ip, timeout_ms), all_ips)
        
        counter = 0
        for ip_str, ping_time in results:
            counter += 1
            if counter % 50 == 0 or counter == total_ips:
                print(f"🔄 پیشرفت: {counter}/{total_ips} آی‌پی تست شد...")
                
            if ping_time is not None:
                healthy_ips.append((ip_str, ping_time))
                print(f"✅ پیدا شد: {ip_str} | پینگ: {ping_time}ms")

    # مرتب‌سازی نتایج بر اساس کمترین پینگ
    healthy_ips.sort(key=lambda x: x[1])

    print("\n" + "="*50)
    print("🏆 نتایج نهایی (۱۵ آی‌پی برتر با کمترین پینگ):")
    print("="*50)
    
    if not healthy_ips:
        print("❌ متاسفانه هیچ آی‌پی سالمی با شرایط شما پیدا نشد.")
    else:
        for index, (ip, ping) in enumerate(healthy_ips[:15], 1):
            print(f"{index:02d}. IP: {ip:<15} | Ping: {ping} ms")
    print("="*50)

if __name__ == "__main__":
    main()