import flet as ft
import socket
import concurrent.futures
import ipaddress

def test_tcp_port(ip_str, port=443, timeout=1.5):
    """Accurate TCP Ping method that works flawlessly on all Android devices"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Start high-resolution timer
        import time
        start_time = time.perf_counter()
        
        result = sock.connect_ex((ip_str, port))
        
        end_time = time.perf_counter()
        sock.close()
        
        if result == 0:
            ping_ms = (end_time - start_time) * 1000
            return ip_str, ping_ms
    except Exception:
        pass
    return ip_str, None

def main(page: ft.Page):
    # App General Settings
    page.title = "ChiliTay Premium Generator"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # UI Elements & Inputs
    config_input = ft.TextField(
        label="Paste Your VLESS / VMess Link",
        placeholder="vless://...",
        border_color="#ff9800",
        focused_border_color="#e65100",
        width=450,
    )

    ranges_input = ft.TextField(
        label="IP Ranges (CIDR)",
        placeholder="e.g. 66.33.22.0/24",
        border_color="#ff9800",
        focused_border_color="#e65100",
        width=450,
    )

    progress_ring = ft.ProgressRing(visible=False, color="#00ffcc")
    status_text = ft.Text(value="", color="#aaa", text_align=ft.TextAlign.CENTER)
    
    output_box = ft.TextField(
        label="Your Top 10 ChiliTay Configs",
        multiline=True,
        min_lines=8,
        max_lines=12,
        read_only=True,
        border_color="#00ffcc",
        width=450,
        visible=False,
    )

    def on_copy_click(e):
        page.set_clipboard(output_box.value)
        page.show_snack_bar(ft.SnackBar(ft.Text("🚀 All configs copied to clipboard!"), open=True))

    copy_button = ft.ElevatedButton(
        text="📋 Copy All Configs",
        color="#121212",
        bgcolor="#00ffcc",
        on_click=on_copy_click,
        visible=False,
        width=250,
    )

    def start_process(e):
        # Reset UI
        output_box.visible = False
        copy_button.visible = False
        progress_ring.visible = True
        status_text.value = "Parsing config link..."
        page.update()

        main_config = config_input.value.strip()
        raw_ranges = ranges_input.value.strip()

        if not main_config or not raw_ranges:
            status_text.value = "❌ Error: Fill all inputs first!"
            progress_ring.visible = False
            page.update()
            return

        # 1. Parse Config
        try:
            prefix, rest = main_config.split("://", 1)
            credentials, connection_details = rest.split("@", 1)
            old_address, after_address = connection_details.split(":", 1)
            
            # Detect port
            if "/" in after_address:
                port_part = after_address.split("/", 1)[0]
            elif "?" in after_address:
                port_part = after_address.split("?", 1)[0]
            elif "#" in after_address:
                port_part = after_address.split("#", 1)[0]
            else:
                port_part = after_address
                
            port = int(port_part) if port_part.isdigit() else 443

            if "#" in after_address:
                params_and_port = after_address.split("#", 1)[0]
            else:
                params_and_port = after_address
        except Exception:
            status_text.value = "❌ Error: Invalid config link format."
            progress_ring.visible = False
            page.update()
            return

        # 2. Extract IPs
        status_text.value = "Extracting IPs from range..."
        page.update()
        
        all_ips = []
        processed_ranges = raw_ranges.replace(",", " ").split()
        for r in processed_ranges:
            try:
                network = ipaddress.ip_network(r.strip(), strict=False)
                all_ips.extend(list(network.hosts()))
            except ValueError:
                continue

        if not all_ips:
            status_text.value = "❌ Error: No valid IP range found."
            progress_ring.visible = False
            page.update()
            return

        status_text.value = f"Scanning {len(all_ips)} IPs via TCP Port {port}..."
        page.update()

        # 3. Parallel Scanning
        healthy_ips = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
            results = executor.map(lambda ip: test_tcp_port(str(ip), port=port), all_ips)
            for ip_str, ping_time in results:
                if ping_time is not None:
                    healthy_ips.append((ip_str, ping_time))

        healthy_ips.sort(key=lambda x: x[1])

        if not healthy_ips:
            status_text.value = "❌ No working IP found on your connection."
            progress_ring.visible = False
            page.update()
            return

        # 4. Generate ChiliTay Configs
        status_text.value = "🎉 Success! Generating your custom configs..."
        generated = []
        for index, (ip, _) in enumerate(healthy_ips[:10], 1):
            config = f"{prefix}://{credentials}@{ip}:{params_and_port}#ChiliTay {index}"
            generated.append(config)

        # 5. Push to UI
        output_box.value = "\n".join(generated)
        output_box.visible = True
        copy_button.visible = True
        progress_ring.visible = False
        status_text.value = f"Found {len(healthy_ips)} clean IPs. Top 10 ready!"
        page.update()

    # Submit Button
    submit_btn = ft.ElevatedButton(
        text="⚡ Build ChiliTay Configs ⚡",
        color="#121212",
        bgcolor="#ff9800",
        width=300,
        height=50,
        on_click=start_process,
    )

    # Adding Everything to Page
    page.add(
        ft.Container(height=20),
        ft.Text("🔥 CHILITAY PREMIUM BUILDER 🔥", size=24, weight=ft.FontWeight.BOLD, color="#ff9800"),
        ft.Text("Graphic Network Scanner & Generator", size=14, color="#888"),
        ft.Container(height=15),
        config_input,
        ranges_input,
        ft.Container(height=10),
        submit_btn,
        ft.Container(height=15),
        progress_ring,
        status_text,
        ft.Container(height=15),
        output_box,
        copy_button,
        ft.Container(height=30),
        ft.Text("Powered by ChiliTay Tools v1.0", size=11, color="#444")
    )

# Run local preview
if __name__ == "__main__":
    ft.app(target=main)