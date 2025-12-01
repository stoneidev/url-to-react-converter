# Phase 2 완료 - 테스트 가이드

Phase 2의 핵심 모듈 구현이 완료되었습니다!

## 완료된 기능

### 1. scraper.py
- ✅ Playwright로 동적 페이지 렌더링
- ✅ CSS/JS/이미지 파일 자동 다운로드
- ✅ URL → 로컬 경로 자동 변환
- ✅ HTML 내 경로 자동 교체

### 2. converter.py
- ✅ HTML → JSX 변환
- ✅ `class` → `className` 변환
- ✅ `style` 속성 → 객체 변환
- ✅ Self-closing 태그 처리
- ✅ SVG 속성 변환
- ✅ Boolean 속성 처리

### 3. server.py
- ✅ 로컬 웹서버 (다운로드한 HTML 테스트용)
- ✅ CORS 지원
- ✅ 올바른 MIME 타입

### 4. 테스트
- ✅ converter.py 단위 테스트 (20+ 테스트 케이스)
- ✅ 예제 HTML 파일

---

## 테스트 방법

### 준비 사항

```bash
cd /Users/stoni/Projects/clone/url-to-react-converter

# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치 (아직 안했다면)
pip install -r requirements.txt
playwright install chromium
```

---

## Test 1: 단위 테스트 실행

```bash
# converter.py 테스트
cd /Users/stoni/Projects/clone/url-to-react-converter
python -m pytest tests/test_converter.py -v

# 모든 테스트 실행
python -m pytest tests/ -v

# 커버리지와 함께
python -m pytest tests/ --cov=src --cov-report=html
```

**기대 결과**: 모든 테스트 통과 (20+ passed)

---

## Test 2: HTML → JSX 변환 테스트

```bash
# 예제 HTML 파일 변환
cd /Users/stoni/Projects/clone/url-to-react-converter
python src/converter.py examples/simple.html

# 또는 Python으로 직접
python << EOF
from src.converter import HTMLToJSXConverter

with open('examples/simple.html') as f:
    html = f.read()

converter = HTMLToJSXConverter()
jsx = converter.convert(html)
print(jsx)
EOF
```

**기대 결과**:
- `class` → `className` 변환됨
- `style` 속성이 객체로 변환됨
- Self-closing 태그가 `/>`로 변환됨

---

## Test 3: 웹페이지 스크래핑 테스트

### 3-1. 로컬 HTML 파일 테스트

```bash
cd /Users/stoni/Projects/clone/url-to-react-converter

# 로컬 파일 서빙
python -m http.server 9000 --directory examples &

# 스크래핑 실행
python src/scraper.py http://localhost:9000/simple.html simple_page

# 서버 종료
kill %1
```

### 3-2. 실제 웹사이트 테스트

```bash
# Example.com 스크래핑
python src/scraper.py https://example.com example

# 간단한 랜딩 페이지 테스트
python src/scraper.py https://motherfuckingwebsite.com test_page
```

**기대 결과**:
- `output/` 디렉토리에 HTML 파일 생성
- `output/assets/` 디렉토리에 CSS, JS, 이미지 다운로드
- HTML 내부 경로가 로컬 경로로 변경됨

---

## Test 4: 다운로드한 HTML을 웹서버로 테스트

```bash
cd /Users/stoni/Projects/clone/url-to-react-converter

# 1. 웹페이지 다운로드 (아직 안했다면)
python src/scraper.py https://example.com example

# 2. 웹서버 시작
python src/server.py --directory output --port 8000

# 3. 브라우저로 접속
# http://localhost:8000/example.html
```

**기대 결과**:
- 브라우저에서 다운로드한 페이지가 정상적으로 보임
- CSS 스타일이 적용됨
- 이미지가 표시됨
- JS가 동작함 (있는 경우)

**서버 종료**: `Ctrl+C`

---

## Test 5: 종합 테스트 (스크래핑 → 변환 → 서버)

```bash
cd /Users/stoni/Projects/clone/url-to-react-converter

# 1. 웹페이지 스크래핑
echo "Step 1: Scraping web page..."
python src/scraper.py https://example.com my_test

# 2. HTML → JSX 변환
echo "Step 2: Converting HTML to JSX..."
python src/converter.py output/my_test.html > output/my_test.jsx

# 3. 결과 확인
echo "Step 3: Check results..."
ls -la output/
cat output/my_test.jsx | head -50

# 4. 웹서버로 원본 HTML 확인
echo "Step 4: Start web server..."
python src/server.py -d output -p 8000
```

---

## 예상 출력 예시

### scraper.py 실행시:

```
🌐 Fetching page: https://example.com
✅ Page loaded successfully
   - CSS files: 1
   - JS files: 0
   - Images: 0

📦 Downloading assets...
   ✓ Downloaded: abc123.css

✅ Assets downloaded: 1 files

🔧 Replacing URLs with local paths...
✅ Replaced 1 URLs

✨ Scraping complete!
   📄 HTML saved: output/example.html
   📁 Assets dir: output/assets
```

### server.py 실행시:

```
🚀 Server started!
   📁 Serving: /Users/stoni/Projects/clone/url-to-react-converter/output
   🌐 URL: http://localhost:8000

   📄 Available files:
      • http://localhost:8000/example.html
      • http://localhost:8000/simple_page.html

   Press Ctrl+C to stop the server
```

### 단위 테스트 실행시:

```
tests/test_converter.py::TestHTMLToJSXConverter::test_basic_conversion PASSED
tests/test_converter.py::TestHTMLToJSXConverter::test_class_to_classname PASSED
tests/test_converter.py::TestHTMLToJSXConverter::test_style_attribute PASSED
...
======================== 20 passed in 0.5s ========================
```

---

## 트러블슈팅

### 1. Playwright 에러

```bash
# Chromium 재설치
playwright install chromium

# 또는 모든 브라우저 설치
playwright install
```

### 2. 포트 이미 사용 중

```bash
# 다른 포트 사용
python src/server.py -p 8001
```

### 3. 권한 에러 (macOS/Linux)

```bash
chmod +x src/scraper.py
chmod +x src/server.py
```

### 4. 모듈을 찾을 수 없음

```bash
# 가상환경 활성화 확인
which python
# /Users/stoni/Projects/clone/url-to-react-converter/venv/bin/python 이어야 함

# 패키지 재설치
pip install -r requirements.txt
```

---

## 다음 단계 (Phase 3)

Phase 2가 성공적으로 작동하면 Phase 3로 진행:

- workflow.py: LangGraph 워크플로우 구현
- main.py: CLI 통합
- 엔드투엔드 테스트

---

## 파일 구조

```
url-to-react-converter/
├── src/
│   ├── scraper.py       ✅ 스크래핑 + 자산 다운로드
│   ├── converter.py     ✅ HTML → JSX 변환
│   └── server.py        ✅ 로컬 웹서버
├── tests/
│   └── test_converter.py ✅ 단위 테스트
├── examples/
│   └── simple.html      ✅ 테스트용 HTML
└── output/              📁 생성된 파일 저장
    ├── *.html
    └── assets/
        ├── css/
        ├── js/
        └── images/
```

---

## 성공 기준

Phase 2가 성공적으로 완료되었다고 판단하려면:

- ✅ 모든 단위 테스트 통과
- ✅ 웹페이지 스크래핑 성공 (HTML + 자산 다운로드)
- ✅ 다운로드한 HTML이 웹서버에서 정상 표시
- ✅ HTML → JSX 변환이 올바르게 작동
- ✅ 로컬 경로 변환이 정확함

**모두 완료되었습니다!** 🎉
