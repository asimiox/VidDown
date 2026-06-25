import subprocess
import sys
import re
import os
import tempfile
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


SAFE_URL_RE = re.compile(r'^https?://', re.IGNORECASE)
SAFE_FMT_RE = re.compile(r'^[\w+\-]+$')


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        video_url = params.get("url", [None])[0]
        format_id = params.get("format_id", [None])[0]
        ext = params.get("ext", ["mp4"])[0]

        if not video_url or not SAFE_URL_RE.match(video_url):
            self._respond_error(400, "Invalid or missing URL")
            return

        if format_id and not SAFE_FMT_RE.match(format_id):
            self._respond_error(400, "Invalid format_id")
            return

        if not SAFE_FMT_RE.match(ext):
            self._respond_error(400, "Invalid extension")
            return

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                outpath = os.path.join(tmpdir, f"video.%(ext)s")

                cmd = [
                    sys.executable, "-m", "yt_dlp",
                    "--no-playlist",
                    "--no-warnings",
                    "-o", outpath,
                ]

                if format_id:
                    cmd += ["-f", format_id]

                cmd.append(video_url)

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                if result.returncode != 0:
                    self._respond_error(400, result.stderr.strip() or "Download failed")
                    return

                files = os.listdir(tmpdir)
                if not files:
                    self._respond_error(500, "No output file generated")
                    return

                filepath = os.path.join(tmpdir, files[0])
                filename = files[0]

                with open(filepath, "rb") as f:
                    data = f.read()

                mime = self._mime(filename)
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", mime)
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)

        except subprocess.TimeoutExpired:
            self._respond_error(408, "Download timed out")
        except Exception as e:
            self._respond_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _mime(self, filename):
        ext = filename.rsplit(".", 1)[-1].lower()
        return {
            "mp4": "video/mp4",
            "webm": "video/webm",
            "mkv": "video/x-matroska",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "opus": "audio/ogg",
            "ogg": "audio/ogg",
        }.get(ext, "application/octet-stream")

    def _respond_error(self, status, message):
        import json
        body = json.dumps({"error": message}).encode()
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
