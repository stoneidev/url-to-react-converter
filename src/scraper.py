"""
웹페이지 스크래핑 모듈
Playwright를 사용하여 동적 페이지 렌더링 및 자산 다운로드
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
import hashlib

from playwright.async_api import async_playwright, Page
import aiohttp
from bs4 import BeautifulSoup


class WebPageScraper:
    """웹페이지 스크래핑 및 자산 다운로드 클래스"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / "assets"

        # 자산 디렉토리 생성
        self.css_dir = self.assets_dir / "css"
        self.js_dir = self.assets_dir / "js"
        self.images_dir = self.assets_dir / "images"

        for directory in [self.css_dir, self.js_dir, self.images_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 수집된 자산 URL 추적
        self.css_files: Set[str] = set()
        self.js_files: Set[str] = set()
        self.images: Set[str] = set()

        # 다운로드 매핑 (원본 URL -> 로컬 경로)
        self.url_to_local: Dict[str, str] = {}

    async def fetch_page(self, url: str) -> Dict:
        """
        URL에서 렌더링된 페이지 가져오기

        Args:
            url: 스크래핑할 URL

        Returns:
            Dict with 'html', 'css_files', 'js_files', 'images'
        """
        print(f"🌐 Fetching page: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 네트워크 요청 모니터링
            page.on('response', lambda response: self._track_assets(response))

            try:
                # 페이지 로드
                await page.goto(url, wait_until='networkidle', timeout=30000)

                # 추가 대기 (동적 콘텐츠)
                await page.wait_for_timeout(2000)

                # 렌더링된 HTML 가져오기
                html = await page.content()

                print(f"✅ Page loaded successfully")
                print(f"   - CSS files: {len(self.css_files)}")
                print(f"   - JS files: {len(self.js_files)}")
                print(f"   - Images: {len(self.images)}")

                return {
                    'html': html,
                    'css_files': list(self.css_files),
                    'js_files': list(self.js_files),
                    'images': list(self.images),
                    'base_url': url
                }

            finally:
                await browser.close()

    def _track_assets(self, response):
        """네트워크 응답에서 자산 파일 추적"""
        url = response.url
        content_type = response.headers.get('content-type', '').lower()

        # CSS 파일
        if 'text/css' in content_type or url.endswith('.css'):
            self.css_files.add(url)

        # JavaScript 파일
        elif 'javascript' in content_type or url.endswith('.js'):
            self.js_files.add(url)

        # 이미지 파일
        elif 'image/' in content_type or any(url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']):
            self.images.add(url)

    async def download_assets(self, base_url: str) -> Dict[str, str]:
        """
        모든 자산 파일 다운로드

        Args:
            base_url: 기본 URL (상대 경로 해결용)

        Returns:
            Dict mapping original URL to local file path
        """
        print(f"\n📦 Downloading assets...")

        async with aiohttp.ClientSession() as session:
            tasks = []

            # CSS 파일 다운로드
            for url in self.css_files:
                absolute_url = urljoin(base_url, url)
                tasks.append(self._download_file(session, absolute_url, self.css_dir, '.css'))

            # JS 파일 다운로드
            for url in self.js_files:
                absolute_url = urljoin(base_url, url)
                tasks.append(self._download_file(session, absolute_url, self.js_dir, '.js'))

            # 이미지 다운로드
            for url in self.images:
                absolute_url = urljoin(base_url, url)
                tasks.append(self._download_file(session, absolute_url, self.images_dir))

            # 병렬 다운로드
            await asyncio.gather(*tasks, return_exceptions=True)

        print(f"✅ Assets downloaded: {len(self.url_to_local)} files")
        return self.url_to_local

    async def _download_file(
        self,
        session: aiohttp.ClientSession,
        url: str,
        output_dir: Path,
        force_extension: str = None
    ):
        """개별 파일 다운로드"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.read()

                    # 파일명 생성 (URL 해시 사용)
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

                    # 확장자 결정
                    if force_extension:
                        extension = force_extension
                    else:
                        parsed = urlparse(url)
                        extension = Path(parsed.path).suffix or '.bin'

                    filename = f"{url_hash}{extension}"
                    filepath = output_dir / filename

                    # 파일 저장
                    filepath.write_bytes(content)

                    # 매핑 저장 (상대 경로)
                    relative_path = filepath.relative_to(self.output_dir)
                    self.url_to_local[url] = str(relative_path)

                    print(f"   ✓ Downloaded: {filename}")

        except Exception as e:
            print(f"   ✗ Failed to download {url}: {e}")

    def _remove_hidden_elements(self, soup: BeautifulSoup) -> int:
        """
        display: none인 캐러셀/슬라이더 요소 제거

        Args:
            soup: BeautifulSoup 객체

        Returns:
            제거된 요소 개수
        """
        removed = 0

        # display: none을 가진 모든 요소 찾기
        # find_all()의 결과를 리스트로 변환하여 수정 중 순회 문제 방지
        elements_with_style = list(soup.find_all(style=True))

        for element in elements_with_style:
            # element가 이미 제거된 경우 건너뛰기
            if not element or not hasattr(element, 'attrs') or not element.attrs:
                continue

            style = element.attrs.get('style', '')
            if not style:
                continue

            # display: none 체크 (공백 무시)
            if 'display' in style and 'none' in style:
                # 간단한 파싱 (CSS 파서 없이)
                style_lower = style.lower().replace(' ', '')
                if 'display:none' in style_lower:
                    # 요소 제거
                    element.decompose()
                    removed += 1

        return removed

    def _remove_duplicate_scripts_and_links(self, soup: BeautifulSoup) -> int:
        """
        중복된 script 및 link 태그 제거

        Args:
            soup: BeautifulSoup 객체

        Returns:
            제거된 요소 개수
        """
        removed = 0

        # 중복 script 태그 제거
        seen_scripts = set()
        for script in list(soup.find_all('script', src=True)):
            if not script or not hasattr(script, 'attrs'):
                continue

            src = script.attrs.get('src', '')
            if not src:
                continue

            if src in seen_scripts:
                # 중복된 스크립트 제거
                script.decompose()
                removed += 1
            else:
                seen_scripts.add(src)

        # 중복 link 태그 제거 (CSS)
        seen_links = set()
        for link in list(soup.find_all('link', href=True)):
            if not link or not hasattr(link, 'attrs'):
                continue

            href = link.attrs.get('href', '')
            rel = link.attrs.get('rel', [])
            if not href:
                continue

            # stylesheet만 체크
            if 'stylesheet' in rel or (isinstance(rel, list) and 'stylesheet' in rel):
                if href in seen_links:
                    # 중복된 링크 제거
                    link.decompose()
                    removed += 1
                else:
                    seen_links.add(href)

        return removed

    def replace_urls_in_html(self, html: str, base_url: str) -> str:
        """
        HTML 내의 URL을 로컬 경로로 변경

        Args:
            html: 원본 HTML
            base_url: 기본 URL

        Returns:
            로컬 경로로 변경된 HTML
        """
        print(f"\n🔧 Replacing URLs with local paths...")

        soup = BeautifulSoup(html, 'html.parser')
        replacements = 0

        # CSS 링크 변경
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                original_url = urljoin(base_url, link['href'])
                if original_url in self.url_to_local:
                    link['href'] = self.url_to_local[original_url]
                    replacements += 1

        # JS 스크립트 변경
        for script in soup.find_all('script', src=True):
            original_url = urljoin(base_url, script['src'])
            if original_url in self.url_to_local:
                script['src'] = self.url_to_local[original_url]
                replacements += 1

        # 이미지 변경
        for img in soup.find_all('img', src=True):
            original_url = urljoin(base_url, img['src'])
            if original_url in self.url_to_local:
                img['src'] = self.url_to_local[original_url]
                replacements += 1

        # srcset 속성도 처리
        for img in soup.find_all('img', srcset=True):
            # srcset은 복잡하므로 간단한 경우만 처리
            pass  # TODO: srcset 처리

        print(f"✅ Replaced {replacements} URLs")

        # 중복 스크립트/링크 제거
        print(f"\n🔧 Removing duplicate scripts and links...")
        removed_duplicates = self._remove_duplicate_scripts_and_links(soup)
        print(f"✅ Removed {removed_duplicates} duplicate script/link tags")

        # 숨겨진 캐러셀/슬라이더 요소 제거
        print(f"\n🧹 Removing hidden carousel elements...")
        removed_hidden = self._remove_hidden_elements(soup)
        print(f"✅ Removed {removed_hidden} hidden elements")

        return str(soup)

    async def scrape_and_save(self, url: str, output_name: str = "index") -> Path:
        """
        완전한 스크래핑 및 저장 프로세스

        Args:
            url: 스크래핑할 URL
            output_name: 출력 파일명 (확장자 제외)

        Returns:
            저장된 HTML 파일 경로
        """
        # 1. 페이지 가져오기
        page_data = await self.fetch_page(url)

        # 2. 자산 다운로드
        await self.download_assets(page_data['base_url'])

        # 3. HTML 내 URL 변경
        modified_html = self.replace_urls_in_html(
            page_data['html'],
            page_data['base_url']
        )

        # 4. HTML 파일 저장
        html_path = self.output_dir / f"{output_name}.html"
        html_path.write_text(modified_html, encoding='utf-8')

        print(f"\n✨ Scraping complete!")
        print(f"   📄 HTML saved: {html_path}")
        print(f"   📁 Assets dir: {self.assets_dir}")

        return html_path


# CLI 사용을 위한 메인 함수
async def main():
    """CLI에서 직접 실행시"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scraper.py <url> [output_name]")
        sys.exit(1)

    url = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "index"

    scraper = WebPageScraper()
    await scraper.scrape_and_save(url, output_name)


if __name__ == "__main__":
    asyncio.run(main())
