# HTML 유사도 검사 가이드

AWS Bedrock Claude를 사용하여 원본 웹페이지와 다운로드된 HTML의 유사도를 자동으로 평가합니다.

## 기능

### 평가 항목

1. **구조적 유사도** (Structural Similarity)
   - HTML 태그 계층 구조
   - 주요 섹션 (header, main, footer 등)
   - 전체 레이아웃 구조

2. **콘텐츠 유사도** (Content Similarity)
   - 텍스트 내용 보존
   - 주요 정보 누락 여부
   - 텍스트 정확도

3. **스타일 보존도** (Style Preservation)
   - CSS 클래스명 유지
   - style 속성 보존
   - 스타일 관련 속성

4. **전체 유사도** (Overall Similarity)
   - 종합 점수 (0-100%)

### 추가 분석

- ❌ 누락된 요소 목록
- ➕ 추가된 요소 목록
- 🔍 주요 차이점
- ✨ 품질 평가 (Good/Fair/Poor)

---

## 사용 방법

### 방법 1: 자동 통합 스크립트 (추천)

웹페이지를 스크래핑하고 자동으로 유사도를 검사합니다.

```bash
cd /Users/stoni/Projects/clone/url-to-react-converter

# 기본 사용
python test_similarity.py https://example.com

# 출력 파일명 지정
python test_similarity.py https://example.com my_test

# 결과 확인
ls -la output/
cat output/my_test_similarity_report.json
```

**출력:**
- `output/my_test.html` - 다운로드된 HTML
- `output/assets/` - CSS, JS, 이미지
- `output/my_test_similarity_report.json` - 유사도 리포트

### 방법 2: 수동 단계별 실행

#### Step 1: 웹페이지 스크래핑

```bash
python src/scraper.py https://example.com example
```

#### Step 2: 유사도 검사

```bash
python src/similarity_checker.py https://example.com output/example.html
```

#### Step 3: 웹서버로 확인

```bash
python src/server.py -d output -p 8000
# 브라우저: http://localhost:8000/example.html
```

---

## 예제 실행

### Example.com 테스트

```bash
# 1. 스크래핑 & 유사도 검사
python test_similarity.py https://example.com example_test

# 2. 결과 확인
cat output/example_test_similarity_report.json | python -m json.tool

# 3. 웹서버로 시각 확인
python src/server.py -d output -p 8000
```

**예상 출력:**

```
🚀 URL to React Converter - Scraping & Similarity Check
======================================================================

📥 Phase 1: Scraping webpage...
   URL: https://example.com

🌐 Fetching page: https://example.com
✅ Page loaded successfully
   - CSS files: 0
   - JS files: 0
   - Images: 0

📦 Downloading assets...
✅ Assets downloaded: 0 files

🔧 Replacing URLs with local paths...
✅ Replaced 0 URLs

✨ Scraping complete!
   📄 HTML saved: output/example_test.html
   📁 Assets dir: output/assets

📊 Phase 2: Checking similarity...

🌐 Fetching original HTML from: https://example.com
✅ Original HTML fetched (1256 chars)
📄 Reading local HTML from: output/example_test.html
✅ Local HTML read (1256 chars)

🔍 Comparing HTML files...

📊 Similarity Analysis Results:
   🏗️  Structural Similarity: 98%
   📝 Content Similarity: 100%
   🎨 Style Preservation: 95%
   🌟 Overall Similarity: 97%
   ✨ Quality: Good

============================================================
📋 DETAILED SIMILARITY REPORT
============================================================

📊 Similarity Scores:
   🏗️  Structural: 98%
   📝 Content: 100%
   🎨 Style: 95%
   ⭐ Overall: 97%

✨ Quality Assessment: Good

🔍 Key Differences:
   - Minor whitespace differences
   - Script execution order may differ

📏 File Sizes:
   Original: 1,256 bytes
   Local: 1,256 bytes

============================================================

🎯 Quick Summary:
   🟢 Overall Similarity: 97% (✅ Excellent)
   📄 Local HTML: output/example_test.html
   📊 Report: output/example_test_similarity_report.json

💡 Test the downloaded HTML:
   python src/server.py -d output -p 8000
   Then open: http://localhost:8000/example_test.html
```

---

## 유사도 리포트 JSON 형식

```json
{
  "structural_similarity": 98,
  "content_similarity": 100,
  "style_preservation": 95,
  "overall_similarity": 97,
  "missing_elements": [],
  "added_elements": [],
  "differences": [
    "Minor whitespace differences",
    "Script execution order may differ"
  ],
  "quality_assessment": "Good",
  "original_url": "https://example.com",
  "local_file": "output/example_test.html",
  "original_size": 1256,
  "local_size": 1256
}
```

---

## 점수 해석

### Overall Similarity

- **90-100%**: 🟢 Excellent - 거의 완벽한 복제
- **70-89%**: 🟡 Good - 잘 작동하지만 일부 차이 있음
- **50-69%**: 🟠 Fair - 주요 내용은 보존되나 개선 필요
- **0-49%**: 🔴 Poor - 상당한 차이, 문제 해결 필요

### Structural Similarity

- **높음 (90%+)**: HTML 구조가 잘 보존됨
- **중간 (70-89%)**: 일부 태그 변경 또는 재배치
- **낮음 (<70%)**: 구조적 변화가 큼

### Content Similarity

- **높음 (90%+)**: 텍스트 내용이 거의 동일
- **중간 (70-89%)**: 일부 텍스트 누락 또는 변경
- **낮음 (<70%)**: 중요 콘텐츠 손실

### Style Preservation

- **높음 (90%+)**: CSS 클래스와 스타일 잘 유지
- **중간 (70-89%)**: 일부 스타일 속성 변경
- **낮음 (<70%)**: 스타일링 상당 부분 손실

---

## 고급 사용

### 다른 모델 사용

```bash
# Claude 3.5 Sonnet v1 사용
python src/similarity_checker.py https://example.com output/example.html \
  --model anthropic.claude-3-5-sonnet-20240620-v1:0

# Claude 3 Opus 사용 (더 강력하지만 비용 높음)
python src/similarity_checker.py https://example.com output/example.html \
  --model anthropic.claude-3-opus-20240229-v1:0

# 다른 리전 사용
python src/similarity_checker.py https://example.com output/example.html \
  --region us-west-2
```

**참고**: Claude 4.x 모델은 inference profile을 통해서만 호출 가능하므로 직접 사용 불가

### Python 코드로 사용

```python
import asyncio
from src.similarity_checker import SimilarityChecker

async def check():
    checker = SimilarityChecker()
    result = await checker.check_similarity(
        "https://example.com",
        "output/example.html"
    )

    print(f"Overall Similarity: {result['overall_similarity']}%")

    # 상세 리포트
    checker.print_detailed_report(result)

    # JSON 저장
    checker.save_report(result, "my_report.json")

asyncio.run(check())
```

---

## 트러블슈팅

### 1. AWS 자격증명 오류

```bash
# AWS 설정 확인
aws configure list

# Bedrock 액세스 확인
aws bedrock list-foundation-models --region us-east-1
```

### 2. Bedrock 모델 액세스 거부

AWS Console에서 Bedrock Model Access 활성화:
https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

### 3. JSON 파싱 에러

Claude의 응답이 JSON 형식이 아닐 수 있습니다. 리포트에 `raw_response` 필드를 확인하세요.

### 4. 네트워크 타임아웃

```bash
# 타임아웃 늘리기 (코드 수정 필요)
# scraper.py에서 timeout=30000 → timeout=60000
```

---

## 제한사항

### 현재 버전의 제한

1. **JavaScript 실행 결과**: JS로 생성된 동적 콘텐츠는 타이밍에 따라 다를 수 있음
2. **외부 리소스**: CDN 장애 등으로 자산 로드 실패 가능
3. **인증 필요 페이지**: 로그인이 필요한 페이지는 지원 안 됨
4. **대용량 페이지**: 매우 큰 페이지는 분석 시간이 오래 걸림

### 비용 고려사항

- Bedrock API 호출당 비용 발생
- **Claude 3.5 Sonnet v2** (기본값): 입력 $3/M tokens, 출력 $15/M tokens
- **Claude 3 Opus**: 입력 $15/M tokens, 출력 $75/M tokens
- **Claude 3 Haiku**: 입력 $0.25/M tokens, 출력 $1.25/M tokens
- 일반적인 페이지: 약 $0.01-0.05 per check (Sonnet 기준)

---

## 실전 팁

### 1. 여러 페이지 일괄 테스트

```bash
#!/bin/bash
urls=(
    "https://example.com"
    "https://example.org"
    "https://example.net"
)

for url in "${urls[@]}"; do
    name=$(echo $url | sed 's/https:\/\///g' | sed 's/\//-/g')
    python test_similarity.py "$url" "$name"
    echo "---"
done
```

### 2. 임계값 기반 자동화

```python
result = await checker.check_similarity(url, local_html)

if result['overall_similarity'] < 70:
    print("⚠️  Quality below threshold!")
    # 재시도 로직 또는 알림
```

### 3. CI/CD 통합

```yaml
# GitHub Actions 예시
- name: Check HTML similarity
  run: |
    python test_similarity.py ${{ env.URL }} test
    SCORE=$(cat output/test_similarity_report.json | jq '.overall_similarity')
    if [ $SCORE -lt 80 ]; then
      echo "Similarity score too low: $SCORE%"
      exit 1
    fi
```

---

## 다음 단계

유사도 검사 후:

1. ✅ 90%+ 점수 → React 변환 진행
2. ⚠️  70-89% 점수 → 누락/변경 사항 확인 후 수동 수정
3. ❌ 70% 미만 → 스크래핑 설정 조정 또는 수동 개입

---

## 관련 파일

- `src/similarity_checker.py` - 유사도 검사 모듈
- `src/scraper.py` - 웹페이지 스크래핑
- `src/server.py` - 로컬 웹서버
- `test_similarity.py` - 통합 테스트 스크립트

---

**작성일**: 2025-12-02
**버전**: 1.0.0
