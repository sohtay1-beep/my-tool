import sys

def main():
    print("\n" + "="*40)
    print("    🔄 AUTO CONFIG IP REPLACER 🔄")
    print("="*40)

    # 1. Get Main Config Link
    print("[*] Paste your main VLESS/VMess/TROJAN config link:")
    main_config = input(" Link: ").strip()

    if not main_config:
        print("[-] Error: Config link cannot be empty.")
        return

    # Parsing the config to inject clean IPs
    try:
        # standard links have format: protocol://uuid@address:port?...#remarks
        if "://" not in main_config or "@" not in main_config:
            print("[-] Error: Invalid config format. Make sure it contains '://' and '@'.")
            return
            
        prefix, rest = main_config.split("://", 1)
        credentials, connection_details = rest.split("@", 1)
        
        # Check if there is a port specified
        if ":" not in connection_details:
            print("[-] Error: Could not find port/address structure in link.")
            return
            
        old_address, after_address = connection_details.split(":", 1)
        
        # Split the remaining part into parameters and remark/name
        if "#" in after_address:
            params_and_port, old_remark = after_address.split("#", 1)
        else:
            params_and_port = after_address
            old_remark = "New-Config"

    except Exception as e:
        print(f"[-] Error parsing config link: {e}")
        return

    # 2. Get Clean IPs
    print("\n[*] Enter clean IPs (Separate them with space or comma):")
    raw_ips = input(" IPs: ")
    clean_ips = raw_ips.replace(",", " ").split()

    if not clean_ips:
        print("[-] Error: No clean IPs provided.")
        return

    print(f"\n[*] Generating {len(clean_ips)} configs...\n")
    print("="*40)
    print("🏆 YOUR NEW CONFIGS:")
    print("="*40 + "\n")

    # 3. Generate new configs
    for index, ip in enumerate(clean_ips, 1):
        new_remark = f"{old_remark}-CleanIP-{index:02d}"
        # Reconstruct the link with the clean IP and updated remark
        new_config = f"{prefix}://{credentials}@{ip}:{params_and_port}#{new_remark}"
        print(f"[+] Config {index:02d}:\n{new_config}\n")
        
    print("="*40)
    print("[*] Done! Copy and paste them into your VPN client.")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
