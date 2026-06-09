import os

def main():
    print("\n" + "="*40)
    print("    🔄 AUTO CONFIG IP REPLACER 🔄")
    print("="*40)

    print("[*] Paste your main VLESS/VMess/TROJAN config link:")
    main_config = input(" Link: ").strip()

    if not main_config:
        print("[-] Error: Config link cannot be empty.")
        return

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
        
        if "#" in after_address:
            params_and_port, old_remark = after_address.split("#", 1)
        else:
            params_and_port = after_address
            old_remark = "New-Config"

    except Exception as e:
        print(f"[-] Error parsing config link: {e}")
        return

    print("\n[*] Enter clean IPs (Separate them with space or comma):")
    raw_ips = input(" IPs: ")
    clean_ips = raw_ips.replace(",", " ").split()

    if not clean_ips:
        print("[-] Error: No clean IPs provided.")
        return

    print(f"\n[*] Generating {len(clean_ips)} configs...")
    
    generated_configs = []

    for index, ip in enumerate(clean_ips, 1):
        new_remark = f"{old_remark}-CleanIP-{index:02d}"
        new_config = f"{prefix}://{credentials}@{ip}:{params_and_port}#{new_remark}"
        generated_configs.append(new_config)

    output_file = "configs.txt"
    all_configs_text = "\n".join(generated_configs)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_configs_text)
    
    print(f"[+] Successfully saved all configs to '{output_file}'")

    print("\n" + "="*40)
    print("📋 QUICK COPY BOX (Double click to select all):")
    print("-" * 40)
    print(all_configs_text)
    print("-" * 40 + "\n")

if __name__ == "__main__":
    main()
