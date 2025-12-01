"""
HTML 유사도 검사 모듈
AWS Bedrock Claude를 사용하여 원본과 다운로드된 HTML의 유사도를 평가
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import boto3
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


class SimilarityChecker:
    """HTML 유사도 검사 클래스"""

    def __init__(
        self,
        model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name: str = "us-east-1"
    ):
        """
        Args:
            model_id: Bedrock 모델 ID
            region_name: AWS 리전
        """
        self.model_id = model_id
        self.region_name = region_name
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )

    async def fetch_original_html(self, url: str) -> str:
        """원본 URL에서 HTML 가져오기"""
        print(f"🌐 Fetching original HTML from: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(1000)
                html = await page.content()
                print(f"✅ Original HTML fetched ({len(html)} chars)")
                return html
            finally:
                await browser.close()

    def read_local_html(self, file_path: str) -> str:
        """로컬 HTML 파일 읽기"""
        print(f"📄 Reading local HTML from: {file_path}")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Local HTML file not found: {file_path}")

        html = path.read_text(encoding='utf-8')
        print(f"✅ Local HTML read ({len(html)} chars)")
        return html

    def _simplify_html(self, html: str) -> str:
        """HTML을 간소화 (비교를 위해)"""
        soup = BeautifulSoup(html, 'html.parser')

        # script와 style 태그 제거 (내용이 달라질 수 있음)
        for tag in soup(['script', 'style']):
            tag.decompose()

        # 주석 제거
        from bs4 import Comment
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 불필요한 공백 제거
        text = str(soup)
        # 여러 공백을 하나로
        import re
        text = re.sub(r'\s+', ' ', text)

        return text

    def _extract_structure(self, html: str) -> str:
        """HTML 구조만 추출 (태그 이름과 계층)"""
        soup = BeautifulSoup(html, 'html.parser')

        def get_structure(element, depth=0):
            if not hasattr(element, 'name') or element.name is None:
                return ""

            indent = "  " * depth
            result = f"{indent}<{element.name}>\n"

            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    result += get_structure(child, depth + 1)

            return result

        body = soup.body if soup.body else soup
        return get_structure(body)

    def _extract_text_content(self, html: str) -> str:
        """HTML에서 텍스트 콘텐츠만 추출"""
        soup = BeautifulSoup(html, 'html.parser')

        # script, style 제거
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()

        # 텍스트 추출
        text = soup.get_text(separator=' ', strip=True)

        # 여러 공백을 하나로
        import re
        text = re.sub(r'\s+', ' ', text)

        return text[:5000]  # 처음 5000자만

    async def compare_html(
        self,
        original_html: str,
        local_html: str
    ) -> Dict:
        """
        두 HTML을 비교하여 유사도 평가

        Args:
            original_html: 원본 HTML
            local_html: 다운로드된 로컬 HTML

        Returns:
            Dict with similarity scores and analysis
        """
        print(f"\n🔍 Comparing HTML files...")

        # HTML 간소화
        original_simple = self._simplify_html(original_html)
        local_simple = self._simplify_html(local_html)

        # 구조 추출
        original_structure = self._extract_structure(original_html)
        local_structure = self._extract_structure(local_html)

        # 텍스트 추출
        original_text = self._extract_text_content(original_html)
        local_text = self._extract_text_content(local_html)

        # Bedrock Claude로 분석
        prompt = f"""두 HTML 파일을 비교하고 유사도를 평가해주세요.

## 원본 HTML 구조:
```
{original_structure[:3000]}
```

## 다운로드된 HTML 구조:
```
{local_structure[:3000]}
```

## 원본 텍스트 콘텐츠:
```
{original_text[:2000]}
```

## 다운로드된 텍스트 콘텐츠:
```
{local_text[:2000]}
```

다음 항목들을 **반드시 JSON 형식**으로 평가해주세요:

1. **structural_similarity**: HTML 구조 유사도 (0-100%)
   - 태그 계층 구조가 얼마나 유사한지
   - 주요 섹션(header, main, footer 등)이 유지되는지

2. **content_similarity**: 콘텐츠 유사도 (0-100%)
   - 텍스트 내용이 얼마나 보존되었는지
   - 주요 정보가 누락되지 않았는지

3. **style_preservation**: 스타일 보존도 (0-100%)
   - CSS 클래스명이 유지되는지
   - style 속성이 보존되는지

4. **overall_similarity**: 전체 유사도 (0-100%)
   - 종합적인 유사도 점수

5. **missing_elements**: 누락된 주요 요소 (배열)
6. **added_elements**: 추가된 요소 (배열)
7. **differences**: 주요 차이점 설명 (배열)
8. **quality_assessment**: 전체 품질 평가 (Good/Fair/Poor)

**응답 형식**:
```json
{{
  "structural_similarity": <숫자>,
  "content_similarity": <숫자>,
  "style_preservation": <숫자>,
  "overall_similarity": <숫자>,
  "missing_elements": [<문자열>],
  "added_elements": [<문자열>],
  "differences": [<문자열>],
  "quality_assessment": "<Good|Fair|Poor>"
}}
```

JSON만 응답하고 다른 설명은 추가하지 마세요.
"""

        try:
            response = self._invoke_bedrock(prompt)

            # JSON 파싱
            # Claude가 ```json ``` 으로 감쌀 수 있으므로 추출
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록이 없으면 전체를 시도
                json_str = response

            result = json.loads(json_str)

            print(f"\n📊 Similarity Analysis Results:")
            print(f"   🏗️  Structural Similarity: {result['structural_similarity']}%")
            print(f"   📝 Content Similarity: {result['content_similarity']}%")
            print(f"   🎨 Style Preservation: {result['style_preservation']}%")
            print(f"   🌟 Overall Similarity: {result['overall_similarity']}%")
            print(f"   ✨ Quality: {result['quality_assessment']}")

            return result

        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse JSON response: {e}")
            print(f"Response: {response[:500]}")

            # 폴백: 기본 응답
            return {
                "structural_similarity": 0,
                "content_similarity": 0,
                "style_preservation": 0,
                "overall_similarity": 0,
                "missing_elements": [],
                "added_elements": [],
                "differences": ["Failed to analyze"],
                "quality_assessment": "Unknown",
                "raw_response": response
            }

    def _invoke_bedrock(self, prompt: str) -> str:
        """Bedrock Claude 호출"""
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    async def check_similarity(
        self,
        original_url: str,
        local_html_path: str
    ) -> Dict:
        """
        전체 유사도 검사 프로세스

        Args:
            original_url: 원본 URL
            local_html_path: 로컬 HTML 파일 경로

        Returns:
            유사도 분석 결과
        """
        print(f"🚀 Starting similarity check...")
        print(f"   Original: {original_url}")
        print(f"   Local: {local_html_path}")

        # 1. 원본 HTML 가져오기
        original_html = await self.fetch_original_html(original_url)

        # 2. 로컬 HTML 읽기
        local_html = self.read_local_html(local_html_path)

        # 3. 비교 분석
        result = await self.compare_html(original_html, local_html)

        # 4. 결과에 메타 정보 추가
        result['original_url'] = original_url
        result['local_file'] = local_html_path
        result['original_size'] = len(original_html)
        result['local_size'] = len(local_html)

        return result

    def save_report(self, result: Dict, output_path: str = "similarity_report.json"):
        """결과를 JSON 파일로 저장"""
        path = Path(output_path)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\n💾 Report saved: {output_path}")

    def print_detailed_report(self, result: Dict):
        """상세 리포트 출력"""
        print(f"\n{'='*60}")
        print(f"📋 DETAILED SIMILARITY REPORT")
        print(f"{'='*60}")

        print(f"\n📊 Similarity Scores:")
        print(f"   🏗️  Structural: {result['structural_similarity']}%")
        print(f"   📝 Content: {result['content_similarity']}%")
        print(f"   🎨 Style: {result['style_preservation']}%")
        print(f"   ⭐ Overall: {result['overall_similarity']}%")

        print(f"\n✨ Quality Assessment: {result['quality_assessment']}")

        if result.get('missing_elements'):
            print(f"\n❌ Missing Elements:")
            for elem in result['missing_elements']:
                print(f"   - {elem}")

        if result.get('added_elements'):
            print(f"\n➕ Added Elements:")
            for elem in result['added_elements']:
                print(f"   - {elem}")

        if result.get('differences'):
            print(f"\n🔍 Key Differences:")
            for diff in result['differences']:
                print(f"   - {diff}")

        print(f"\n📏 File Sizes:")
        print(f"   Original: {result.get('original_size', 0):,} bytes")
        print(f"   Local: {result.get('local_size', 0):,} bytes")

        print(f"\n{'='*60}")


async def main():
    """CLI에서 직접 실행"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Check similarity between original and downloaded HTML"
    )
    parser.add_argument('url', help='Original URL')
    parser.add_argument('local_html', help='Local HTML file path')
    parser.add_argument(
        '-o', '--output',
        default='similarity_report.json',
        help='Output report file (default: similarity_report.json)'
    )
    parser.add_argument(
        '--model',
        default='us.anthropic.claude-sonnet-4-5-v1:0',
        help='Bedrock model ID'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region'
    )

    args = parser.parse_args()

    checker = SimilarityChecker(
        model_id=args.model,
        region_name=args.region
    )

    result = await checker.check_similarity(args.url, args.local_html)
    checker.print_detailed_report(result)
    checker.save_report(result, args.output)


if __name__ == "__main__":
    asyncio.run(main())
