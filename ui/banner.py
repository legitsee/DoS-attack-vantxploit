import os, sys, time, random
from ui.colors import *

INTRO_ART = [
    r"  ____   ____            __               .__          .__  __",
    r"  \   \ /   /____  _____/  |___ ______  __|  |   ____ |__|/  |_",
    r"   \   Y   /\__  \ \  \_\   __\  \  \/\/  /  |  /  _ \|  \   __\\",
    r"    \     /  / __ \_/  | \  | |  |\      /|  |_(  <_> )  ||  |",
    r"     \___/  (____  /\__| |__| |__| \/\/  |____/\____/|__||__|",
    r"                 \/",
]

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def hex_matrix(rows=16):
    chars = "0123456789ABCDEFabcdef"
    palette = [VD, DP, P, BV, GY, DG]
    for _ in range(rows):
        line = "".join(random.choice(chars) for _ in range(72))
        col = random.choice(palette)
        sys.stdout.write(f"\r  {col}{line}{RS}")
        sys.stdout.flush()
        time.sleep(0.018)
    print()

def glitch_decode(text, delay=0.018):
    pool = "0123456789ABCDEF!@#$%^&*<>[]|?/\\"
    for i in range(1, len(text) + 1):
        rev = text[:i]
        noise = "".join(random.choice(pool) for _ in range(min(5, len(text) - i)))
        sys.stdout.write(f"\r  {W}{B}{rev}{BV}{noise}{RS}    ")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def vantx_intro():
    clear()
    hex_matrix(18)
    time.sleep(0.04)
    clear()
    print("\n")
    for line in INTRO_ART:
        col = random.choice([BV, P, DP, LV]) if random.random() > 0.25 else INV
        if col == INV:
            sys.stdout.write(f"  {INV}{line}{RS}\n")
        else:
            sys.stdout.write(f"  {col}{B}{line}{RS}\n")
        time.sleep(0.06)
    time.sleep(0.3)
    print()
    glitch_decode("> DoS Vantxploit v4.0  —  Real Engine loaded.", 0.015)
    glitch_decode("> Strike protocol initialized. Awaiting target.", 0.015)
    time.sleep(0.4)
    clear()

def ascii_header():
    ln = chr(0x2550)
    tl = chr(0x2554); tr = chr(0x2557)
    ml = chr(0x2560); mr = chr(0x2563)
    bl = chr(0x255A); br = chr(0x255D)
    vl = chr(0x2551)
    print()
    print(f"  {DP}{tl}{ln*68}{tr}{RS}")
    print(f"  {DP}{vl}{RS}  {BV}{B}{'VANTXPLOIT':^68}{RS}  {DP}{vl}{RS}")
    print(f"  {DP}{ml}{ln*68}{mr}{RS}")
    print(f"  {DP}{vl}{RS}  {LV}{B}{'v4.0  Real Engine':^20}{RS}  {GY}|{RS}  {W}{'Multi-Vector Strike Suite':^25}{RS}  {GY}|{RS}  {DG}{'Real HTTP Flood':^14}{RS}  {DP}{vl}{RS}")
    print(f"  {DP}{bl}{ln*68}{br}{RS}")
    print()

def fake_progress(label, width=36, color=P):
    for i in range(width + 1):
        bar = chr(0x2588) * i + chr(0x2591) * (width - i)
        pct = int((i / width) * 100)
        sys.stdout.write(f"\r  {GY}[{ts()}]{RS}  {color}{label}{RS}  [{color}{bar}{RS}] {W}{B}{pct:3d}%{RS}")
        sys.stdout.flush()
        time.sleep(random.uniform(0.018, 0.055))
    print()

def ts():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

def dt():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def startup_messages():
    for msg in [
        "Loading Vantxploit strike modules...",
        "Initializing real HTTP engine (asyncio)...",
        "Resolving target DNS records...",
        "Loading User-Agent pool (204 entries)...",
        "Arming multi-vector flood arsenal...",
        "All systems operational. Awaiting command.",
    ]:
        print(f"  {GY}[{ts()}]{RS}  {G}[+]{RS}  {W}{msg}{RS}")
        time.sleep(0.22)
    time.sleep(0.3)
