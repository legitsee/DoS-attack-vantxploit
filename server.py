#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver

PORT = 8080
WEBSITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website")

class LoggingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBSITE_DIR, **kwargs)

    def log_message(self, format, *args):
        ip, *_ = self.client_address
        msg = format % args
        status = args[1] if len(args) > 1 else "-"
        color = "\033[38;2;220;50;50m" if status >= "500" else (
            "\033[38;2;220;140;20m" if status >= "400" else "\033[38;2;40;200;80m"
        )
        rs = "\033[0m"
        gy = "\033[38;2;90;75;105m"
        print(f"  {gy}[{self.log_date_time_string()}]{rs}  {color}[{msg}]{rs}  {gy}{ip}{rs}")

def main():
    print(f"\n  \033[38;2;100;0;160m{'═' * 60}\033[0m")
    print(f"  \033[38;2;55;0;90m║\033[0m  \033[38;2;140;30;200m\033[1mVANTXPLOIT — Demo HTTP Server\033[0m")
    print(f"  \033[38;2;100;0;160m{'═' * 60}\033[0m")
    print(f"  \033[38;2;55;0;90m║\033[0m  \033[38;2;120;80;150mHosting\033[0m:  \033[38;2;210;200;215m{WEBSITE_DIR}\033[0m")
    print(f"  \033[38;2;55;0;90m║\033[0m  \033[38;2;120;80;150mURL\033[0m:     \033[38;2;180;120;220mhttp://localhost:{PORT}\033[0m")
    print(f"  \033[38;2;55;0;90m║\033[0m  \033[38;2;120;80;150mHit Ctrl+C\033[0m to stop")
    print(f"  \033[38;2;100;0;160m{'═' * 60}\033[0m\n")

    with socketserver.TCPServer(("", PORT), LoggingHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n  \033[38;2;220;190;0m[*] Server stopped.\033[0m\n")
            httpd.server_close()
            sys.exit(0)

if __name__ == "__main__":
    main()
