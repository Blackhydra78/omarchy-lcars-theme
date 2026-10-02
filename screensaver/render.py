#!/usr/bin/env python3
"""Render warp.html to enterprise-warp.mp4.

Serves this directory over localhost, drives headless Chromium through
capture.html (which steps warp.html frame by frame and POSTs each canvas as a
PNG), then encodes the frames with ffmpeg.

Usage: render.py [--width 2560] [--height 1600] [--fps 60] [--seconds 12]
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=2560)
    ap.add_argument("--height", type=int, default=1600)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--seconds", type=int, default=12)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--software", action="store_true", help="render with SwiftShader instead of the GPU")
    ap.add_argument("--output", default=str(HERE / "enterprise-warp.mp4"))
    args = ap.parse_args()

    total = args.fps * args.seconds
    frames = Path(tempfile.mkdtemp(prefix="lcars-frames-"))
    done = threading.Event()
    failed = []

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(HERE), **kw)

        def log_message(self, *a):
            pass

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            if self.path.startswith("/frame/"):
                n = int(self.path.rsplit("/", 1)[1])
                (frames / f"{n:05d}.png").write_bytes(body)
                if n % 30 == 0:
                    print(f"frame {n}/{total}", flush=True)
            elif self.path == "/done":
                done.set()
            elif self.path == "/error":
                failed.append(body.decode(errors="replace"))
                done.set()
            self.send_response(204)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    gl = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] if args.software else ["--use-angle=default", "--ignore-gpu-blocklist", "--enable-gpu"]
    profile = tempfile.mkdtemp(prefix="lcars-chromium-")
    url = f"http://127.0.0.1:{port}/capture.html?w={args.width}&h={args.height}&fps={args.fps}&frames={total}"
    browser = subprocess.Popen(
        ["chromium", "--headless=new", "--no-sandbox", f"--user-data-dir={profile}", *gl,
         f"--window-size={args.width},{args.height}", "--force-device-scale-factor=1", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        while not done.wait(1):
            if browser.poll() is not None:
                failed.append(f"chromium exited with {browser.returncode}")
                break
    finally:
        browser.terminate()
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)

    count = len(list(frames.glob("*.png")))
    if failed or count != total:
        shutil.rmtree(frames, ignore_errors=True)
        sys.exit(f"render failed ({count}/{total} frames): {'; '.join(failed)}")

    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps), "-i", str(frames / "%05d.png"),
         "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", args.output],
        check=True,
    )
    shutil.rmtree(frames, ignore_errors=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
