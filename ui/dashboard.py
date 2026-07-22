import sys
import time
import threading
from ui.colors import *
from core.stats import AttackStats

class Dashboard:
    def __init__(self, stats: AttackStats, duration=None, mode: str = "HTTP Flood"):
        self.stats = stats
        self.duration = duration
        self.mode = mode
        self._running = False
        self._thread = None

    def _render(self):
        block = chr(0x2588)
        light = chr(0x2591)
        while self._running:
            s = self.stats.snapshot()
            elapsed = int(s["elapsed"])
            bw = 34
            if self.duration is None:
                remain = "--"
                bar = f"{BV}{block * bw}{RS}"
            else:
                remain = max(0, self.duration - elapsed)
                done = min(bw, int((elapsed / self.duration) * bw)) if self.duration > 0 else 0
                bar = f"{BV}{block * done}{DG}{light * (bw - done)}{RS}"

            line1 = (
                f"{DP}\u2551{RS}  "
                f"{GY}REQ/S:{RS}{W}{B}{s['req_per_sec']:>10.1f}{RS}  "
                f"{GY}LAT:{RS}{BV}{B}{s['avg_latency']:>8.1f}ms{RS}  "
                f"{GY}CONN:{RS}{MV}{B}{s['active_connections']:>5}{RS}  "
                f"[{bar}] {Y}{B}{remain:>3}{RS}  "
                f"{DP}\u2551{RS}"
            )
            line2 = (
                f"{DP}\u2551{RS}  "
                f"{G}{B}2xx:{RS}{W}{s['successful']:>8,}{RS}  "
                f"{O}{B}4xx:{RS}{W}{s['client_errors']:>8,}{RS}  "
                f"{R}{B}5xx:{RS}{W}{s['server_errors']:>8,}{RS}  "
                f"{Y}{B}T/O:{RS}{W}{s['timeouts']:>8,}{RS}  "
                f"{R}{B}ERR:{RS}{W}{s['connection_errors']:>8,}{RS}  "
                f"{DP}\u2551{RS}"
            )
            line3 = (
                f"{DP}\u2551{RS}  "
                f"{GY}SENT:{RS}{LV}{B}{s['bytes_sent'] / (1024**2):>7.2f} MB{RS}  "
                f"{GY}RECV:{RS}{LV}{B}{s['bytes_received'] / (1024**2):>7.2f} MB{RS}  "
                f"{GY}BW↑:{RS}{BV}{B}{s['bandwidth_sent']:>6.2f} MB/s{RS}  "
                f"{DP}\u2551{RS}"
            )

            sys.stdout.write(f"\r  {line1}\n  {line2}\n  {line3}\n")
            sys.stdout.flush()
            time.sleep(0.3)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._render, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def show_header(self, target_url: str):
        tl = chr(0x2554); tr = chr(0x2557)
        ml = chr(0x2560); mr = chr(0x2563)
        bl = chr(0x255A); br = chr(0x255D)
        vl = chr(0x2551); ln = chr(0x2550)

        print()
        print(f"  {DP}{tl}{ln*68}{tr}{RS}")
        print(f"  {DP}{vl}{RS}  {BV}{B}{'>>> VANTXPLOIT — STRIKE PROTOCOL ACTIVE <<<':^68}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{ml}{ln*68}{mr}{RS}")
        print(f"  {DP}{vl}{RS}  {GY}TARGET   :{RS}  {W}{B}{target_url:<56}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{vl}{RS}  {GY}MODE     :{RS}  {BV}{B}{self.mode:<56}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{vl}{RS}  {GY}DURATION :{RS}  {MV}{B}{('INF' if self.duration is None else str(self.duration) + 's'):<56}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{vl}{RS}  {GY}STARTED  :{RS}  {W}{time.strftime('%Y-%m-%d %H:%M:%S'):<56}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{bl}{ln*68}{br}{RS}\n")

    def show_report(self):
        s = self.stats.snapshot()
        tl = chr(0x2554); tr = chr(0x2557)
        ml = chr(0x2560); mr = chr(0x2563)
        bl = chr(0x255A); br = chr(0x255D)
        vl = chr(0x2551); ln = chr(0x2550)

        print()
        print(f"  {DP}{tl}{ln*68}{tr}{RS}")
        print(f"  {DP}{vl}{RS}  {LV}{B}{'STRIKE COMPLETE — VANTXPLOIT MISSION REPORT':^68}{RS}  {DP}{vl}{RS}")
        print(f"  {DP}{ml}{ln*68}{mr}{RS}")

        rows = [
            ("Total Requests", f"{s['total_requests']:,}", W),
            ("Successful (2xx)", f"{s['successful']:,}", G),
            ("Client Errors (4xx)", f"{s['client_errors']:,}", O),
            ("Server Errors (5xx)", f"{s['server_errors']:,}", R),
            ("Timeouts", f"{s['timeouts']:,}", Y),
            ("Connection Errors", f"{s['connection_errors']:,}", R),
            ("Avg Latency", f"{s['avg_latency']} ms", BV),
            ("Min / Max Latency", f"{s['min_latency']} / {s['max_latency']} ms", MV),
            ("Peak Requests/s", str(s['req_per_sec']), BV),
            ("Data Sent", f"{s['bytes_sent'] / (1024**2):.2f} MB", LV),
            ("Data Received", f"{s['bytes_received'] / (1024**2):.2f} MB", LV),
            ("Bandwidth Sent", f"{s['bandwidth_sent']} MB/s", BV),
        ]
        for label, value, color in rows:
            print(f"  {DP}{vl}{RS}  {GY}{label:<20}:{RS}  {color}{B}{value:<44}{RS}  {DP}{vl}{RS}")

        print(f"  {DP}{bl}{ln*68}{br}{RS}")
        print()
