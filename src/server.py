"""
로컬 웹 서버 - 다운로드한 HTML 및 자산을 서빙하기 위한 간단한 서버
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import argparse


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """MIME 타입 및 인코딩을 올바르게 처리하는 핸들러"""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }

    def end_headers(self):
        """CORS 헤더 추가 (로컬 테스트용)"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        """로그 메시지 포맷팅"""
        print(f"[{self.address_string()}] {format % args}")


def serve(directory: str = "./output", port: int = 8000):
    """
    지정된 디렉토리에서 웹 서버 시작

    Args:
        directory: 서빙할 디렉토리
        port: 포트 번호
    """
    # 디렉토리 존재 확인
    serve_dir = Path(directory).resolve()
    if not serve_dir.exists():
        print(f"❌ Error: Directory '{directory}' does not exist")
        sys.exit(1)

    # 디렉토리로 이동
    os.chdir(serve_dir)

    # 서버 시작
    handler = CustomHTTPRequestHandler
    server_address = ('', port)

    try:
        httpd = HTTPServer(server_address, handler)
        print(f"\n🚀 Server started!")
        print(f"   📁 Serving: {serve_dir}")
        print(f"   🌐 URL: http://localhost:{port}")
        print(f"\n   📄 Available files:")

        # HTML 파일 목록 표시
        html_files = list(serve_dir.glob("*.html"))
        if html_files:
            for html_file in html_files:
                print(f"      • http://localhost:{port}/{html_file.name}")
        else:
            print(f"      (No HTML files found)")

        print(f"\n   Press Ctrl+C to stop the server\n")

        httpd.serve_forever()

    except KeyboardInterrupt:
        print(f"\n\n✋ Server stopped")
        httpd.shutdown()

    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {port} is already in use")
            print(f"   Try a different port: python server.py --port 8001")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        description="Start a local web server to test downloaded HTML"
    )
    parser.add_argument(
        '-d', '--directory',
        default='./output',
        help='Directory to serve (default: ./output)'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        help='Port number (default: 8000)'
    )

    args = parser.parse_args()

    serve(args.directory, args.port)


if __name__ == "__main__":
    main()
