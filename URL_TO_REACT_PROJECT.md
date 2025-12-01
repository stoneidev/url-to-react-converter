# URL to React Converter - Agentic AI 프로젝트

## 프로젝트 개요

특정 URL의 웹페이지를 입력받아 React/Next.js 코드로 자동 변환하는 LangGraph 기반 Agentic AI 시스템

### 핵심 전략
- **페이지 단위 변환**: 전체 사이트가 아닌 지정된 단일 페이지만 변환
- **JS 로직 유지**: 기존 JavaScript 파일은 그대로 사용
- **HTML DOM → React 집중**: HTML 구조를 JSX로 변환하는 것에 주력
- **CSS 유지**: 기존 스타일시트 그대로 사용

### 기대 효과
- 기술적 가능성: **95%**
- 시간 절감: **60-80%** (수동 변환 대비)
- 코드 품질: **70%** (사람의 검토 및 개선 필요)

---

## 3단계 로드맵

### 1단계: HTML/Static 파일 복제 (가능성: 90%)
- Puppeteer/Playwright로 렌더링된 페이지 추출
- 이미지, CSS, JS 등 static 자산 다운로드
- 로컬에 완전한 복제본 생성

### 2단계: React 변환 (가능성: 90%)
- HTML DOM → JSX 변환
- CSS/JS 파일은 그대로 유지
- Next.js 프로젝트 구조로 생성
- **사람 개입**: 컴포넌트 구조 개선, state 관리, 이벤트 핸들러 최적화

### 3단계: 리팩토링 (사람 주도)
- 의미적 컴포넌트 분리
- Props 설계
- React 패턴 적용
- 성능 최적화

---

## 기술 스택

### 핵심 프레임워크
- **LangGraph**: 워크플로우 오케스트레이션
- **LangChain AWS**: LLM 통합
- **AWS Bedrock (Claude)**: 코드 생성 및 개선

### 크롤링/파싱
- **Playwright** 또는 **Puppeteer**: 동적 페이지 렌더링
- **BeautifulSoup4**: HTML 파싱
- **lxml**: XML/HTML 처리

### 코드 생성
- **Babel**: JSX 문법 검증
- **Prettier**: 코드 포맷팅
- **ESLint**: 문법 검증

---

## LangGraph 아키텍처

### State 정의

```python
from typing import TypedDict, List

class ConversionState(TypedDict):
    # 입력
    url: str
    component_name: str

    # 1단계: 스크래핑
    html: str
    css_files: List[str]
    js_files: List[str]
    images: List[str]

    # 2단계: 파싱
    dom_tree: dict

    # 3단계: 변환
    jsx_code: str

    # 4단계: 생성
    component_code: str
    css_code: str

    # 검증
    errors: List[str]
    build_success: bool
```

### 워크플로우 그래프

```
[Start]
   ↓
[fetch_page] ─────→ Playwright로 페이지 렌더링
   ↓
[extract_assets] ─→ CSS, JS, 이미지 파일 추출
   ↓
[download_assets] → 로컬에 자산 다운로드
   ↓
[parse_dom] ──────→ HTML 구조 파싱
   ↓
[convert_to_jsx] ─→ HTML → JSX 규칙 기반 변환
   ↓
[enhance_jsx] ────→ LLM으로 코드 개선
   ↓
[generate_files] ─→ React 컴포넌트 파일 생성
   ↓
[validate_jsx] ───→ JSX 문법 검증
   ↓
   ├─→ [에러 있음] → [fix_errors] ─┐
   │                               ↓
   └─→ [에러 없음] ────────────→ [END]
```

---

## 핵심 변환 로직

### HTML → JSX 규칙 기반 변환

```python
def html_to_jsx_rules():
    """
    확정적으로 변환 가능한 규칙들 (LLM 불필요)
    """
    return {
        # 속성 변환
        'class': 'className',
        'for': 'htmlFor',
        'tabindex': 'tabIndex',
        'readonly': 'readOnly',
        'maxlength': 'maxLength',
        'cellpadding': 'cellPadding',
        'cellspacing': 'cellSpacing',
        'rowspan': 'rowSpan',
        'colspan': 'colSpan',

        # SVG 속성
        'stroke-width': 'strokeWidth',
        'stroke-linecap': 'strokeLinecap',
        'fill-opacity': 'fillOpacity',
        'stop-color': 'stopColor',

        # Self-closing tags
        'void_elements': [
            'area', 'base', 'br', 'col', 'embed', 'hr',
            'img', 'input', 'link', 'meta', 'param',
            'source', 'track', 'wbr'
        ]
    }

def convert_style_attribute(style_string):
    """
    style="color: red; font-size: 14px"
    →
    style={{color: 'red', fontSize: '14px'}}
    """
    if not style_string:
        return None

    style_obj = {}
    for rule in style_string.split(';'):
        if ':' in rule:
            prop, value = rule.split(':', 1)
            prop = prop.strip()
            value = value.strip()

            # kebab-case → camelCase
            prop_camel = ''.join(
                word.capitalize() if i > 0 else word
                for i, word in enumerate(prop.split('-'))
            )

            style_obj[prop_camel] = value

    return style_obj

def convert_element_to_jsx(element):
    """
    BeautifulSoup element → JSX string
    """
    tag = element.name

    # Self-closing 처리
    if tag in void_elements and not element.contents:
        return f"<{tag} {convert_attributes(element.attrs)} />"

    # 일반 요소
    jsx = f"<{tag} {convert_attributes(element.attrs)}>"

    for child in element.children:
        if isinstance(child, str):
            jsx += escape_jsx_text(child)
        else:
            jsx += convert_element_to_jsx(child)

    jsx += f"</{tag}>"
    return jsx
```

### JavaScript 통합 전략

#### Option A: 외부 스크립트 로드

```jsx
import { useEffect } from 'react'

export default function Page() {
  useEffect(() => {
    // 기존 JS 파일 동적 로드
    const script = document.createElement('script')
    script.src = '/assets/js/original.js'
    script.async = true
    document.body.appendChild(script)

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  return <div>{/* JSX */}</div>
}
```

#### Option B: 인라인 스크립트 실행

```jsx
useEffect(() => {
  // 기존 인라인 스크립트 실행
  window.initializeWidget = function() {
    // 원래 스크립트 내용
  }

  window.initializeWidget()
}, [])
```

#### Option C: 이벤트 핸들러 변환 (LLM 필요)

```html
<!-- Before -->
<button onclick="handleClick('value')">Click</button>
```

```jsx
// After
<button onClick={() => handleClick('value')}>Click</button>
```

---

## 상세 구현 계획

### Phase 1: 프로젝트 설정 (1일)

#### AWS Bedrock 사전 요구사항

```bash
# 1. AWS CLI 설치 및 설정
aws --version
aws configure
# AWS Access Key ID, Secret Access Key, Region (us-east-1) 입력

# 2. Bedrock 모델 액세스 활성화
# AWS Console에서 Bedrock > Model access 메뉴에서 Claude 모델 활성화
# https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

# 3. 모델 액세스 확인
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')]"
```

#### Python 환경 설정

```bash
mkdir url-to-react-converter
cd url-to-react-converter

# Python 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Phase 2: 핵심 모듈 구현 (3-5일)

#### 1. 페이지 스크래퍼 (`scraper.py`)

```python
from playwright.async_api import async_playwright
from typing import Dict, List
import asyncio

async def fetch_page(url: str) -> Dict:
    """
    주어진 URL의 렌더링된 HTML과 자산 정보 추출
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 네트워크 요청 모니터링
        css_files = []
        js_files = []
        images = []

        page.on('response', lambda response:
            track_assets(response, css_files, js_files, images)
        )

        await page.goto(url, wait_until='networkidle')

        # 렌더링된 HTML
        html = await page.content()

        await browser.close()

        return {
            'html': html,
            'css_files': css_files,
            'js_files': js_files,
            'images': images
        }

def track_assets(response, css_files, js_files, images):
    """네트워크 응답에서 자산 파일 추적"""
    url = response.url
    content_type = response.headers.get('content-type', '')

    if 'text/css' in content_type:
        css_files.append(url)
    elif 'javascript' in content_type:
        js_files.append(url)
    elif 'image/' in content_type:
        images.append(url)
```

#### 2. HTML → JSX 변환기 (`converter.py`)

```python
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, Any

class HTMLToJSXConverter:
    """HTML을 JSX로 변환하는 클래스"""

    ATTR_MAP = {
        'class': 'className',
        'for': 'htmlFor',
        'tabindex': 'tabIndex',
        # ... 전체 매핑
    }

    VOID_ELEMENTS = {
        'img', 'br', 'hr', 'input', 'meta', 'link',
        'area', 'base', 'col', 'embed', 'param',
        'source', 'track', 'wbr'
    }

    def convert(self, html: str) -> str:
        """HTML 문자열을 JSX로 변환"""
        soup = BeautifulSoup(html, 'lxml')
        body = soup.body

        if not body:
            return ""

        return self._convert_element(body)

    def _convert_element(self, element) -> str:
        """단일 요소를 JSX로 변환"""
        if isinstance(element, NavigableString):
            return self._escape_text(str(element))

        tag = element.name
        attrs = self._convert_attributes(element.attrs)

        # Self-closing 태그
        if tag in self.VOID_ELEMENTS and not element.contents:
            return f"<{tag}{attrs} />"

        # 일반 태그
        children = ''.join(
            self._convert_element(child)
            for child in element.children
        )

        return f"<{tag}{attrs}>{children}</{tag}>"

    def _convert_attributes(self, attrs: Dict) -> str:
        """HTML 속성을 JSX 속성으로 변환"""
        if not attrs:
            return ""

        jsx_attrs = []

        for key, value in attrs.items():
            # 속성명 변환
            jsx_key = self.ATTR_MAP.get(key, key)

            # 특수 처리: style
            if jsx_key == 'style' and isinstance(value, str):
                value = self._convert_style(value)
                jsx_attrs.append(f'{jsx_key}={{{value}}}')

            # Boolean 속성
            elif value is True or value == key:
                jsx_attrs.append(jsx_key)

            # 일반 속성
            elif isinstance(value, list):
                jsx_attrs.append(f'{jsx_key}="{" ".join(value)}"')
            else:
                jsx_attrs.append(f'{jsx_key}="{value}"')

        return ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''

    def _convert_style(self, style_str: str) -> str:
        """
        style="color: red; font-size: 14px"
        → {{color: 'red', fontSize: '14px'}}
        """
        style_obj = {}

        for rule in style_str.split(';'):
            if ':' not in rule:
                continue

            prop, val = rule.split(':', 1)
            prop = prop.strip()
            val = val.strip()

            # kebab-case → camelCase
            prop_camel = self._to_camel_case(prop)
            style_obj[prop_camel] = val

        # 객체를 문자열로
        items = [f"{k}: '{v}'" for k, v in style_obj.items()]
        return '{' + ', '.join(items) + '}'

    def _to_camel_case(self, kebab: str) -> str:
        """kebab-case → camelCase"""
        parts = kebab.split('-')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])

    def _escape_text(self, text: str) -> str:
        """JSX 텍스트 이스케이핑"""
        # {, } 처리
        text = text.replace('{', '&#123;')
        text = text.replace('}', '&#125;')
        return text
```

#### 3. LangGraph 워크플로우 (`workflow.py`)

```python
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, List

class State(TypedDict):
    url: str
    component_name: str
    html: str
    css_files: List[str]
    js_files: List[str]
    jsx_code: str
    component_code: str
    errors: List[str]

def create_converter_workflow():
    workflow = StateGraph(State)

    # === 노드 정의 ===

    async def fetch_page_node(state: State) -> State:
        """페이지 스크래핑"""
        result = await fetch_page(state["url"])
        return {**state, **result}

    def parse_and_convert_node(state: State) -> State:
        """HTML → JSX 변환"""
        converter = HTMLToJSXConverter()
        jsx = converter.convert(state["html"])
        return {**state, "jsx_code": jsx}

    async def enhance_with_llm_node(state: State) -> State:
        """LLM으로 코드 개선"""
        from langchain_aws import ChatBedrock

        llm = ChatBedrock(
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name="us-east-1"
        )

        prompt = f"""
다음 JSX 코드를 개선해주세요:

```jsx
{state["jsx_code"]}
```

개선 요구사항:
1. 인라인 이벤트 핸들러를 React 방식으로 변환
2. 반복되는 패턴이 있다면 .map() 사용
3. key props 추가 (필요시)
4. 불필요한 div 래핑 제거
5. 접근성 개선 (aria-* 속성)

주의사항:
- className, style 등 기존 속성은 유지
- 구조를 크게 변경하지 말 것
- 코드만 출력 (설명 불필요)
"""

        response = await llm.ainvoke(prompt)
        enhanced_jsx = response.content

        return {**state, "jsx_code": enhanced_jsx}

    def generate_component_node(state: State) -> State:
        """최종 React 컴포넌트 생성"""
        name = state["component_name"]
        jsx = state["jsx_code"]
        js_files = state["js_files"]

        # JS 로더 생성
        js_loader = ""
        if js_files:
            js_loader = f"""
  useEffect(() => {{
    const scripts = {js_files};
    const scriptElements = scripts.map(src => {{
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      return script;
    }});

    scriptElements.forEach(script => document.body.appendChild(script));

    return () => {{
      scriptElements.forEach(script => document.body.removeChild(script));
    }};
  }}, []);
"""

        component = f"""import {{ useEffect }} from 'react';
import './{name}.css';

export default function {name}() {{
{js_loader}
  return (
    {jsx}
  );
}}
"""

        return {**state, "component_code": component}

    def validate_node(state: State) -> State:
        """JSX 문법 검증"""
        try:
            # Babel이나 ESLint로 검증
            # 여기서는 간단히 기본 체크만
            jsx = state["jsx_code"]

            errors = []

            # 기본 JSX 규칙 체크
            if '<>' in jsx and not '</>' in jsx:
                errors.append("Fragment not closed")

            # 속성 체크
            if 'class=' in jsx:
                errors.append("Use className instead of class")

            return {**state, "errors": errors}
        except Exception as e:
            return {**state, "errors": [str(e)]}

    async def fix_errors_node(state: State) -> State:
        """에러 수정"""
        from langchain_aws import ChatBedrock

        llm = ChatBedrock(
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name="us-east-1"
        )

        prompt = f"""
다음 JSX 코드에 에러가 있습니다:

```jsx
{state["jsx_code"]}
```

에러 목록:
{chr(10).join(f"- {e}" for e in state["errors"])}

에러를 수정한 코드만 출력해주세요.
"""

        response = await llm.ainvoke(prompt)
        fixed_jsx = response.content

        return {**state, "jsx_code": fixed_jsx, "errors": []}

    # === 노드 등록 ===
    workflow.add_node("fetch", fetch_page_node)
    workflow.add_node("convert", parse_and_convert_node)
    workflow.add_node("enhance", enhance_with_llm_node)
    workflow.add_node("generate", generate_component_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("fix", fix_errors_node)

    # === 엣지 정의 ===
    workflow.set_entry_point("fetch")
    workflow.add_edge("fetch", "convert")
    workflow.add_edge("convert", "enhance")
    workflow.add_edge("enhance", "generate")
    workflow.add_edge("generate", "validate")

    # 조건부 엣지
    workflow.add_conditional_edges(
        "validate",
        lambda state: "fix" if state["errors"] else "end",
        {
            "fix": "fix",
            "end": END
        }
    )
    workflow.add_edge("fix", "validate")

    return workflow.compile()
```

#### 4. CLI 인터페이스 (`main.py`)

```python
import asyncio
import argparse
from pathlib import Path

async def convert_url_to_react(
    url: str,
    component_name: str,
    output_dir: str = "./output"
):
    """메인 변환 함수"""

    print(f"🚀 Converting {url} to React component...")

    # 워크플로우 실행
    workflow = create_converter_workflow()

    result = await workflow.ainvoke({
        "url": url,
        "component_name": component_name
    })

    # 파일 저장
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 컴포넌트 파일
    component_file = output_path / f"{component_name}.jsx"
    component_file.write_text(result["component_code"])

    print(f"✅ Component saved: {component_file}")

    # CSS 파일 (간단히 링크만)
    css_file = output_path / f"{component_name}.css"
    css_content = f"/* CSS files from original page:\n"
    for css in result["css_files"]:
        css_content += f" * {css}\n"
    css_content += " */\n\n/* Add your styles here */"
    css_file.write_text(css_content)

    print(f"✅ CSS template saved: {css_file}")
    print(f"\n🎉 Conversion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert web page to React component"
    )
    parser.add_argument("url", help="URL to convert")
    parser.add_argument(
        "-n", "--name",
        default="Page",
        help="Component name (default: Page)"
    )
    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory (default: ./output)"
    )

    args = parser.parse_args()

    asyncio.run(convert_url_to_react(
        args.url,
        args.name,
        args.output
    ))
```

### Phase 3: 테스트 (2-3일)

```python
# tests/test_converter.py
import pytest
from converter import HTMLToJSXConverter

def test_basic_conversion():
    html = '<div class="container"><p>Hello</p></div>'
    converter = HTMLToJSXConverter()
    jsx = converter.convert(html)

    assert 'className="container"' in jsx
    assert '<p>Hello</p>' in jsx

def test_style_conversion():
    html = '<div style="color: red; font-size: 14px"></div>'
    converter = HTMLToJSXConverter()
    jsx = converter.convert(html)

    assert 'color: \'red\'' in jsx
    assert 'fontSize: \'14px\'' in jsx

def test_self_closing_tags():
    html = '<img src="test.jpg" alt="Test">'
    converter = HTMLToJSXConverter()
    jsx = converter.convert(html)

    assert '<img' in jsx
    assert '/>' in jsx

@pytest.mark.asyncio
async def test_full_workflow():
    from workflow import create_converter_workflow

    workflow = create_converter_workflow()

    # 간단한 HTML로 테스트
    result = await workflow.ainvoke({
        "url": "https://example.com",
        "component_name": "ExamplePage"
    })

    assert result["component_code"]
    assert "export default function ExamplePage" in result["component_code"]
```

---

## MVP 범위 및 제약사항

### MVP에 포함할 기능

✅ **필수 기능**
- [x] 단일 URL 입력 → React 컴포넌트 생성
- [x] HTML DOM → JSX 변환
- [x] CSS 파일 링크 추출
- [x] JS 파일 링크 추출
- [x] 기본 속성 변환 (class → className)
- [x] Self-closing 태그 처리
- [x] Style 속성 객체 변환
- [x] Next.js 프로젝트 구조 생성

✅ **Nice to have**
- [ ] 인라인 이벤트 핸들러 변환
- [ ] 반복 패턴 → .map() 변환
- [ ] 이미지 자동 다운로드
- [ ] CSS 파일 자동 다운로드

### MVP에서 제외할 기능

❌ **제외 (나중에)**
- jQuery → React 변환
- 복잡한 상태 관리
- 서버 사이드 렌더링 설정
- TypeScript 지원
- 자동 테스트 생성
- 반응형 개선
- 접근성 자동 개선

---

## 예상 도전과제 및 해결 방안

### 1. 동적 콘텐츠 처리

**문제**: AJAX로 로드되는 콘텐츠
**해결**:
```python
# Playwright에서 특정 selector 대기
await page.wait_for_selector('.dynamic-content', timeout=5000)
await page.wait_for_load_state('networkidle')
```

### 2. 인라인 이벤트 핸들러

**문제**: `onclick="handleClick()"`
**해결**: LLM에게 변환 요청
```python
prompt = """
Convert inline event handlers to React:
<button onclick="alert('hi')">Click</button>
→
<button onClick={() => alert('hi')}>Click</button>
"""
```

### 3. Form 요소

**문제**: `<input value="...">`는 React에서 controlled component
**해결**: 일단 기본값으로 변환, 나중에 사람이 state 추가
```jsx
// 1차 변환 (작동은 함)
<input defaultValue="test" />

// 사람이 개선
const [value, setValue] = useState("test")
<input value={value} onChange={e => setValue(e.target.value)} />
```

### 4. CSS 클래스명 충돌

**문제**: 여러 페이지를 변환하면 클래스명 충돌 가능
**해결**: CSS Modules 사용
```jsx
import styles from './Page.module.css'

<div className={styles.container}>
```

### 5. 성능 최적화

**문제**: 큰 페이지는 변환 시간 오래 걸림
**해결**:
- 병렬 처리 (자산 다운로드)
- 캐싱 (같은 URL 재요청 방지)
- 스트리밍 (부분적으로 결과 반환)

---

## 다음 단계 (우선순위)

### 즉시 시작 가능
1. [ ] 프로젝트 디렉토리 구조 생성
2. [ ] `scraper.py` 구현 (Playwright)
3. [ ] `converter.py` 기본 변환 로직
4. [ ] 단순 테스트 페이지로 검증

### 1주일 내
5. [ ] LangGraph 워크플로우 통합
6. [ ] LLM 개선 단계 추가
7. [ ] CLI 인터페이스 완성
8. [ ] 실제 웹사이트로 테스트

### 2주일 내
9. [ ] Next.js 프로젝트 생성 자동화
10. [ ] CSS/JS 자산 다운로드
11. [ ] 에러 처리 개선
12. [ ] 문서화 및 사용 가이드

---

## 프로젝트 구조

```
url-to-react-converter/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── scraper.py          # Playwright 스크래핑
│   ├── converter.py        # HTML → JSX 변환
│   ├── workflow.py         # LangGraph 워크플로우
│   ├── validators.py       # JSX 검증
│   └── utils.py            # 유틸리티 함수
│
├── tests/
│   ├── test_scraper.py
│   ├── test_converter.py
│   └── test_workflow.py
│
├── examples/
│   ├── simple_page.html
│   └── expected_output.jsx
│
├── templates/
│   ├── nextjs_template/    # Next.js 프로젝트 템플릿
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── pages/
│   └── component_template.jsx
│
└── output/                  # 생성된 파일 출력
    └── .gitkeep
```

---

## 사용 예시

### 기본 사용법

```bash
# 설치
pip install -r requirements.txt
playwright install chromium

# AWS 설정 확인 (default profile 사용)
aws configure list

# 또는 환경변수로 설정
export AWS_PROFILE=default
export AWS_REGION=us-east-1

# 변환 실행
python main.py https://example.com/pricing -n PricingPage

# 출력 확인
ls output/
# → PricingPage.jsx
# → PricingPage.css
```

### 프로그래밍 방식

```python
from workflow import create_converter_workflow

async def main():
    workflow = create_converter_workflow()

    result = await workflow.ainvoke({
        "url": "https://example.com/about",
        "component_name": "AboutPage"
    })

    print(result["component_code"])

asyncio.run(main())
```

---

## 참고 자료

### 공식 문서
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Playwright Python](https://playwright.dev/python/)
- [React 문서](https://react.dev/)
- [Next.js 문서](https://nextjs.org/docs)

### 유사 프로젝트
- [html-to-react](https://github.com/milesj/html-to-react)
- [Screenshot to Code](https://github.com/abi/screenshot-to-code)
- [v0.dev by Vercel](https://v0.dev/)

### 기술 아티클
- [HTML to JSX 변환 가이드](https://transform.tools/html-to-jsx)
- [LangGraph 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/)

---

## 라이선스 및 주의사항

### 법적 고려사항
⚠️ **중요**: 웹 스크래핑시 주의사항
- robots.txt 확인
- 저작권 및 이용 약관 준수
- Rate limiting (요청 제한)
- 개인정보 처리 주의

### 윤리적 사용
- 공개된 웹사이트만 변환
- 상업적 사용시 원 저작자에게 허가 받기
- 내부 도구/학습 목적으로 사용 권장

---

## 변경 이력

- **2025-12-02**: 초기 프로젝트 설계 문서 작성
- 다음 업데이트: 구현 진행 상황 및 테스트 결과 추가 예정

---

## 기여 방법

이 프로젝트를 개선하려면:
1. 이슈 생성하여 버그 리포트 또는 기능 제안
2. Fork 후 feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 제출

---

**프로젝트 상태**: 설계 단계 ✏️
**다음 마일스톤**: MVP 구현 (예상 2주)
