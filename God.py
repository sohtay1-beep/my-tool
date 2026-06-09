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
    print("\n" + "="*50)
    print("    🔥 ALL-IN-ONE CONFIG AUTO-GENERATOR 🔥")
    print("="*50)

    # 1. Get Main Config
    print("[*] Paste your main VLESS/VMess/TROJAN config link:")
    main_config = input(" Link: ").strip()

    if not main_config:
        print("[-] Error: Config link cannot be empty.")
        return

    # Parse config
    try:
        if "://" not in main_config or "@" not in main_config:
            print("[-] Error: Invalid config format.")
            return
        prefix, rest = main_config.split("://", 1)
        credentials, connection_details = rest.split("@", 1)
        if ":" not in connection_details:
            print("[-] Error: Could not find port/address structure.")
            return
        old_address, after_address = connection_details.split(":", 1)
        
        # We only need the parameters part before the '#' symbol
        if "#" in after_address:
            params_and_port, _ = after_address.split("#", 1)
        else:
            params_and_port = after_address
    except Exception as e:
        print(f"[-] Error parsing config link: {e}")
        return

    # 2. Get IP Ranges
    print("\n[*] Enter IP Ranges (CIDR):")
    raw_ranges = input(" IP Ranges: ")
    processed_ranges = raw_ranges.replace(",", " ").split()
    
    if not processed_ranges:
        print("[-] Error: No IP ranges entered.")
        return

    # Settings
    threads_input = input("Threads [Default 50]: ")
    max_threads = int(threads_input) if threads_input.strip().isdigit() else 50

    timeout_input = input("Timeout MS [Default 1500]: ")
    timeout_ms = int(timeout_input) if timeout_input.strip().isdigit() else 1500

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
        
    print(f"\n[*] Extracted {total_ips} IPs. Starting scanner...")
    print(f"[*] Scanning with {max_threads} threads...\n")
    
    healthy_ips = []
    
    # 3. Scan IPs
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(lambda ip: ping_ip(ip, timeout_ms), all_ips)
        
        counter = 0
        for ip_str, ping_time in results:
            counter += 1
            if counter % 50 == 0 or counter == total_ips:
                print(f"[>] Progress: {counter}/{total_ips}")
                
            if ping_time is not None:
                healthy_ips.append((ip_str, ping_time))

    # Sort by lowest ping
    healthy_ips.sort(key=lambda x: x[1])

    if not healthy_ips:
        print("\n[-] Error: No clean IP found on your network. Cannot generate configs.\n")
        return

    # Take top 10 best IPs
    top_ips = healthy_ips[:10]
    print(f"\n[+] Found {len(top_ips)} clean IPs. Generating configs...")

    # 4. Generate Final Configs with Custom Remark (ChiliTay X)
    generated_configs = []
    for index, (ip, ping) in enumerate(top_ips, 1):
        new_remark = f"ChiliTay {index}"
        new_config = f"{prefix}://{credentials}@{ip}:{params_and_port}#{new_remark}"
        generated_configs.append(new_config)

    # Save to file
    all_configs_text = "\n".join(generated_configs)
    output_file = "auto_configs.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_configs_text)
        
    print(f"[+] All configs saved to '{output_file}'")

    # 5. Output Clean Copy Box
    print("\n" + "="*50)
    print("🏆 YOUR TOP 10 AUTO-GENERATED CONFIGS:")
    print("="*50)
    print(all_configs_text)
    print("="*50 + "\n")
    print("💡 Double click the box above to select and copy all 10 configs!")

if __name__ == "__main__":
    main()
