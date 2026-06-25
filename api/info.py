import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "url" not in params:
            self._respond(400, {"error": "Missing 'url' parameter"})
            return

        video_url = params["url"][0]

        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp",
                    "--dump-json",
                    "--no-playlist",
                    "--no-warnings",
                    video_url,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self._respond(400, {"error": result.stderr.strip() or "Could not fetch video info"})
                return

            info = json.loads(result.stdout)

            formats = []
            seen = set()

            for f in info.get("formats", []):
                fmt_id = f.get("format_id", "")
                ext = f.get("ext", "")
                vcodec = f.get("vcodec", "none")
                acodec = f.get("acodec", "none")
                height = f.get("height")
                filesize = f.get("filesize") or f.get("filesize_approx")
                tbr = f.get("tbr")

                if vcodec != "none" and acodec != "none":
                    kind = "video+audio"
                elif vcodec != "none":
                    kind = "video"
                elif acodec != "none":
                    kind = "audio"
                else:
                    continue

                label = f"{height}p" if height else ext.upper()
                key = f"{kind}-{label}-{ext}"
                if key in seen:
                    continue
                seen.add(key)

                size_str = None
                if filesize:
                    mb = filesize / (1024 * 1024)
                    size_str = f"{mb:.1f} MB"

                formats.append({
                    "format_id": fmt_id,
                    "ext": ext,
                    "kind": kind,
                    "label": label,
                    "resolution": f"{height}p" if height else None,
                    "size": size_str,
                    "tbr": tbr,
                })

            formats.sort(key=lambda x: (
                0 if x["kind"] == "video+audio" else (1 if x["kind"] == "video" else 2),
                -(x.get("tbr") or 0)
            ))

            response = {
                "title": info.get("title", "Unknown"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "platform": info.get("extractor_key", "Unknown"),
                "formats": formats[:30],
            }

            self._respond(200, response)

        except subprocess.TimeoutExpired:
            self._respond(408, {"error": "Request timed out. Try again."})
        except json.JSONDecodeError:
            self._respond(500, {"error": "Could not parse video data"})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._set_cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
