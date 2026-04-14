#!/usr/bin/env python3
"""
講義建立 本地伺服器
用法：python3 server.py
"""
import http.server
import json
import os
import subprocess
import base64
import tempfile
import re
from urllib.parse import urlparse

PORT = 8765
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTLINES_DIR = os.path.join(PROJECT_ROOT, '_outlines')


def parse_outline(content):
    """Parse _outlines/*.md into structured data."""
    result = {'meta': {}, 'parts': []}

    # Frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).split('\n'):
            m = re.match(r'^(\w+):\s*(.+)$', line.strip())
            if m:
                result['meta'][m.group(1)] = m.group(2).strip('"\'')

    # Parts & chapters
    current_part = None
    for line in content.split('\n'):
        part_m = re.match(r'^## (Part \d+)：(.+?)(?:（(.+?)）)?$', line)
        if part_m:
            current_part = {
                'num': part_m.group(1),
                'title': part_m.group(2).strip(),
                'duration': part_m.group(3) or '',
                'chapters': []
            }
            result['parts'].append(current_part)
        elif current_part:
            ch_m = re.match(r'^- (CH\d+-\d+|PRAC\d+)：(.+)$', line)
            if ch_m:
                current_part['chapters'].append({
                    'id': ch_m.group(1),
                    'title': ch_m.group(2).strip()
                })
    return result


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default logging

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            self._serve_file('index.html')
        elif path == '/api/courses':
            self._api_courses()
        elif path.startswith('/api/outline/'):
            self._api_outline(path.split('/')[-1])
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        if path == '/api/convert':
            self._api_convert(data)
        elif path == '/api/save-outline':
            self._api_save_outline(data)
        elif path == '/api/launch':
            self._api_launch(data)
        else:
            self.send_response(404)
            self.end_headers()

    # ── static ──────────────────────────────────────────────────────────────

    def _serve_file(self, filename):
        filepath = os.path.join(SCRIPT_DIR, filename)
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            return
        with open(filepath, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    # ── API ─────────────────────────────────────────────────────────────────

    def _api_courses(self):
        courses = []
        skip = {'講義建立', '素材', '_規範', '_outlines', '_進度'}
        for name in sorted(os.listdir(PROJECT_ROOT)):
            full = os.path.join(PROJECT_ROOT, name)
            if (os.path.isdir(full)
                    and not name.startswith('.')
                    and name not in skip
                    and os.path.exists(os.path.join(full, 'index.html'))):
                outline_path = os.path.join(OUTLINES_DIR, f'{name}.md')
                courses.append({'slug': name, 'has_outline': os.path.exists(outline_path)})
        self.send_json(courses)

    def _api_outline(self, slug):
        # Sanitize slug
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        path = os.path.join(OUTLINES_DIR, f'{slug}.md')
        if not os.path.exists(path):
            self.send_json({'error': 'not found'}, 404)
            return
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.send_json(parse_outline(content))

    def _api_convert(self, data):
        file_b64 = data.get('file', '')
        if not file_b64:
            self.send_json({'error': 'no file'}, 400)
            return
        try:
            file_bytes = base64.b64decode(file_b64)
        except Exception as e:
            self.send_json({'error': f'base64 decode failed: {e}'}, 400)
            return

        tmp = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        try:
            tmp.write(file_bytes)
            tmp.close()
            result = subprocess.run(
                ['pandoc', tmp.name, '-t', 'markdown', '--wrap=none'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self.send_json({'error': result.stderr}, 500)
            else:
                self.send_json({'markdown': result.stdout})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
        finally:
            os.unlink(tmp.name)

    def _api_save_outline(self, data):
        slug = re.sub(r'[^a-z0-9\-]', '', data.get('slug', '').strip())
        content = data.get('content', '').strip()
        if not slug or not content:
            self.send_json({'error': 'missing slug or content'}, 400)
            return
        os.makedirs(OUTLINES_DIR, exist_ok=True)
        path = os.path.join(OUTLINES_DIR, f'{slug}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.send_json({'ok': True})

    def _api_launch(self, data):
        action = data.get('action', '')
        slug = re.sub(r'[^a-z0-9\-_]', '', data.get('slug', ''))

        if action == 'step':
            ch = re.sub(r'[^A-Z0-9\-]', '', data.get('ch', ''))
            title = data.get('title', '').replace('"', "'")
            prompt = f'/build-course-page step {slug} {ch} "{title}"'
        elif action == 'overview':
            module_n = re.sub(r'[^0-9]', '', str(data.get('module', '1')))
            prompt = f'/build-course-page overview {slug} module{module_n}'
        elif action == 'update-cards':
            target = os.path.basename(data.get('target', 'module1.html'))
            prompt = f'/build-course-page update-cards {slug}/{target}'
        else:
            prompt = '/build-course-page'

        # Escape for AppleScript / shell double-quoting
        proj = PROJECT_ROOT.replace('\\', '\\\\').replace('"', '\\"')
        cmd = prompt.replace('\\', '\\\\').replace('"', '\\"')

        apple_script = (
            f'tell application "Terminal"\n'
            f'  activate\n'
            f'  do script "cd \\"{proj}\\" && claude \\"{cmd}\\""\n'
            f'end tell'
        )

        try:
            subprocess.run(['osascript', '-e', apple_script], check=True, timeout=10)
            self.send_json({'ok': True, 'prompt': prompt})
        except subprocess.CalledProcessError as e:
            self.send_json({'error': f'osascript failed: {e}'}, 500)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)


if __name__ == '__main__':
    print(f'講義建立伺服器啟動：http://localhost:{PORT}')
    print(f'專案路徑：{PROJECT_ROOT}')
    print('按 Ctrl+C 停止\n')
    server = http.server.HTTPServer(('localhost', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n伺服器已停止')
