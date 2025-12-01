#!/usr/bin/env python
"""
웹페이지 스크래핑 후 유사도 자동 검사 스크립트
"""

import asyncio
import sys
from pathlib import Path

from src.scraper import WebPageScraper
from src.similarity_checker import SimilarityChecker


async def scrape_and_check(url: str, output_name: str = "test"):
    """
    웹페이지를 스크래핑하고 유사도를 자동으로 검사

    Args:
        url: 스크래핑할 URL
        output_name: 출력 파일명
    """
    print("="*70)
    print("🚀 URL to React Converter - Scraping & Similarity Check")
    print("="*70)

    # 1. 웹페이지 스크래핑
    print(f"\n📥 Phase 1: Scraping webpage...")
    print(f"   URL: {url}")

    scraper = WebPageScraper(output_dir="./output")
    html_path = await scraper.scrape_and_save(url, output_name)

    print(f"\n✅ Scraping complete!")
    print(f"   HTML saved: {html_path}")
    print(f"   Assets saved: {scraper.assets_dir}")

    # 2. 유사도 검사
    print(f"\n📊 Phase 2: Checking similarity...")

    checker = SimilarityChecker()
    result = await checker.check_similarity(url, str(html_path))

    # 3. 상세 리포트 출력
    checker.print_detailed_report(result)

    # 4. JSON 리포트 저장
    report_path = f"output/{output_name}_similarity_report.json"
    checker.save_report(result, report_path)

    # 5. 결과 요약
    print(f"\n🎯 Quick Summary:")
    overall = result['overall_similarity']

    if overall >= 90:
        status = "✅ Excellent"
        color = "🟢"
    elif overall >= 70:
        status = "✓ Good"
        color = "🟡"
    elif overall >= 50:
        status = "⚠️  Fair"
        color = "🟠"
    else:
        status = "❌ Poor"
        color = "🔴"

    print(f"   {color} Overall Similarity: {overall}% ({status})")
    print(f"   📄 Local HTML: {html_path}")
    print(f"   📊 Report: {report_path}")

    print(f"\n💡 Test the downloaded HTML:")
    print(f"   python src/server.py -d output -p 8000")
    print(f"   Then open: http://localhost:8000/{output_name}.html")

    return result


async def main():
    """CLI 메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: python test_similarity.py <url> [output_name]")
        print("\nExamples:")
        print("  python test_similarity.py https://example.com")
        print("  python test_similarity.py https://example.com my_test")
        sys.exit(1)

    url = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "test"

    try:
        await scrape_and_check(url, output_name)
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
