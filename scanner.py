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
    print("\n" + "="*40)
    print("      ⚡ FASTLY & VERCEL SCANNER ⚡")
    print("="*40)
    
    # 1. IP Input
    raw_ranges = input("IP Ranges (CIDR): ")
    processed_ranges = raw_ranges.replace(",", " ").split()
    
    if not processed_ranges:
        print("[-] Error: No IP ranges entered.")
        return

    # 2. Threads Input
    threads_input = input("Threads [Default 50]: ")
    try:
        max_threads = int(threads_input) if threads_input.strip() else 50
    except ValueError:
        max_threads = 50

    # 3. Timeout Input
    timeout_input = input("Timeout MS [Default 1500]: ")
    try:
        timeout_ms = int(timeout_input) if timeout_input.strip() else 1500
    except ValueError:
        timeout_ms = 1500

    # Extract IPs
    all_ips = []
    for r in processed_ranges:
        try:
            network = ipaddress.ip_network(r.strip(), strict=False)
            all_ips.extend(list(network.hosts()))
        except ValueError:
            print(f"[-] Invalid range skipped: {r}")
            
    total_ips = len(all_ips)
    if total_ips == 0:
        print("[-] Error: No valid IPs found.")
        return
        
    print(f"\n[*] Total IPs: {total_ips}")
    print(f"[*] Scanning with {max_threads} threads...\n")
    
    healthy_ips = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(lambda ip: ping_ip(ip, timeout_ms), all_ips)
        
        counter = 0
        for ip_str, ping_time in results:
            counter += 1
            if counter % 50 == 0 or counter == total_ips:
                print(f"[>] Progress: {counter}/{total_ips}")
                
            if ping_time is not None:
                healthy_ips.append((ip_str, ping_time))
                print(f" [+] Found: {ip_str:<15} | Ping: {ping_time}ms")

    healthy_ips.sort(key=lambda x: x[1])

    print("\n" + "="*40)
    print("🏆 TOP 15 BEST IPs:")
    print("="*40)
    
    if not healthy_ips:
        print("[-] No clean IP found on your network.")
    else:
        for index, (ip, ping) in enumerate(healthy_ips[:15], 1):
            print(f" {index:02d} -> {ip:<15} | {ping} ms")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
