# URL to React Converter - TODO List

## Phase 1: 프로젝트 설정 (1일)

### AWS Bedrock 사전 요구사항
프로젝트 시작 전에 AWS 설정이 필요합니다:

```bash
# AWS CLI 설치 확인
aws --version

# AWS 자격증명 설정 (이미 설정된 경우 생략)
aws configure
# AWS Access Key ID, Secret Access Key, Region (us-east-1 권장) 입력

# Bedrock 모델 액세스 확인
aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?contains(modelId, 'claude')]"

# Claude 모델 사용 권한 확인 (콘솔에서 model access 활성화 필요)
# https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
```

- [x] 1. 프로젝트 디렉토리 구조 생성 및 초기 설정
  ```bash
  mkdir -p url-to-react-converter/{src,tests,templates,output,examples}
  cd url-to-react-converter
  ```

- [x] 2. Python 가상환경 생성 및 필수 패키지 설치 (setup.sh 스크립트 제공)
  ```bash
  # 자동 설정 스크립트 실행
  ./setup.sh

  # 또는 수동으로:
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  playwright install chromium
  ```

- [x] 3. requirements.txt 파일 작성
  - langgraph
  - langchain-aws
  - boto3
  - playwright
  - beautifulsoup4
  - lxml
  - pytest
  - pytest-asyncio

- [x] 4. .env.example 파일 생성 (AWS Bedrock 설정)
  - AWS_PROFILE=default (또는 명시적으로 지정)
  - AWS_REGION=us-east-1 (Bedrock 사용 가능 리전)
  - BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

---

## Phase 2: 핵심 모듈 구현 (3-5일)

### scraper.py
- [x] 5. Playwright로 페이지 렌더링 및 HTML 추출 기능 구현
- [x] 6. CSS/JS/이미지 파일 URL 추출 기능 추가 (네트워크 모니터링)
- [x] 6-1. 중복 스크립트/링크 제거 기능 추가
- [x] 6-2. display:none 요소 제거 기능 추가
- [x] 6-3. JS 동적 렌더링 컨테이너 비우기 기능 추가

### converter.py
- [x] 7. HTMLToTSXConverter 클래스 구현 (속성 변환 로직)
  - `class` → `className`
  - `for` → `htmlFor`
  - 기타 HTML → TSX 속성 매핑

- [x] 8. style 속성 객체 변환 기능 추가
  - `style="color: red"` → `style={{color: 'red'}}`
  - kebab-case → camelCase 변환

- [x] 9. self-closing 태그 처리 추가
  - `<img>` → `<img />`
  - void elements 처리

- [x] 10. converter.py 단위 테스트 작성 및 실행

### 추가 완료 항목
- [x] server.py 구현 (로컬 웹서버)
- [x] similarity_checker.py 구현 (HTML 유사도 검사)
- [x] 중복 렌더링 문제 해결 (3가지 원인 모두 수정)

---

## Phase 3: LangGraph 워크플로우 (3-4일)

### workflow.py
- [ ] 11. State TypedDict 정의
  - url, component_name, html, css_files, js_files, jsx_code, component_code, errors

- [ ] 12. fetch_page_node 노드 구현
  - scraper.py의 fetch_page 함수 호출
  - State에 결과 저장

- [ ] 13. parse_and_convert_node 노드 구현
  - HTMLToJSXConverter 사용
  - HTML → JSX 변환

- [ ] 14. enhance_with_llm_node 노드 구현 (Claude API 연동)
  - 인라인 이벤트 핸들러 개선
  - 반복 패턴 → .map() 변환
  - key props 추가

- [ ] 15. generate_component_node 노드 구현
  - React 컴포넌트 템플릿 생성
  - useEffect로 JS 파일 로드
  - import 문 추가

- [ ] 16. validate_node 노드 구현 (JSX 문법 검증)
  - 기본 JSX 규칙 체크
  - class vs className 검사

- [ ] 17. fix_errors_node 노드 구현
  - LLM으로 에러 수정

- [ ] 18. LangGraph 엣지 및 조건부 엣지 설정
  - 워크플로우 컴파일

---

## Phase 4: CLI 및 통합 (1-2일)

### main.py
- [ ] 19. CLI 인터페이스 및 argparse 설정
  - url, --name, --output 인자 처리

- [ ] 20. 파일 저장 로직 추가 (컴포넌트, CSS 파일)
  - output 디렉토리 생성
  - .jsx, .css 파일 저장

---

## Phase 5: 테스트 및 완성 (2-3일)

- [ ] 21. 간단한 HTML 페이지로 엔드투엔드 테스트
  - 로컬 HTML 파일로 테스트
  - 기본 변환 확인

- [ ] 22. 실제 웹사이트 URL로 테스트 및 결과 검증
  - example.com 같은 간단한 사이트
  - 랜딩 페이지

- [ ] 23. 생성된 React 컴포넌트 빌드 테스트 (Next.js 환경)
  - Next.js 프로젝트 생성
  - 생성된 컴포넌트 import
  - npm run build 실행

- [ ] 24. 에러 처리 개선 및 로깅 추가
  - try-except 블록
  - 상세한 에러 메시지
  - 진행 상황 로깅

- [x] 25. README.md 작성 (설치 및 사용 가이드)
  - 설치 방법
  - 사용 예시
  - 제약사항

---

## 완료된 작업

### Phase 1: 프로젝트 설정 ✅
- [x] 프로젝트 설계 문서 작성 (URL_TO_REACT_PROJECT.md)
- [x] TODO 리스트 생성 (TODO.md)
- [x] requirements.txt 작성 (AWS Bedrock 기반)
- [x] .env.example 작성 (AWS 설정 템플릿)
- [x] 프로젝트 디렉토리 구조 생성
- [x] setup.sh 자동 설정 스크립트 작성
- [x] .gitignore 작성
- [x] README.md 작성
- [x] 모델을 Claude Sonnet 4.5로 변경

### Phase 2: 핵심 모듈 구현 ✅
- [x] scraper.py 구현 (Playwright 스크래핑, 자산 다운로드, 경로 변환)
  - [x] 중복 스크립트/링크 제거 기능
  - [x] display:none 요소 제거 기능
  - [x] JS 동적 렌더링 컨테이너 비우기 기능
- [x] server.py 구현 (로컬 웹서버)
- [x] converter.py 구현 (HTML → TSX 완전 변환)
- [x] converter.py 단위 테스트 작성 (20+ 테스트 케이스)
- [x] similarity_checker.py 구현 (AWS Bedrock Claude를 이용한 HTML 유사도 검사)
- [x] 예제 HTML 파일 생성 (simple.html)
- [x] Phase 2 테스트 가이드 작성 (PHASE2_TESTING.md)
- [x] 유사도 검사 가이드 작성 (SIMILARITY_CHECK_GUIDE.md)
- [x] 중복 렌더링 문제 완전 해결 (3가지 원인 모두 수정)

---

## 우선순위 (다음에 할 일)

### 🔥 High Priority (즉시 시작)
1. 프로젝트 디렉토리 구조 생성
2. Python 가상환경 설정 및 패키지 설치
3. scraper.py 기본 구현

### ⚡ Medium Priority (1주일 내)
4. converter.py 구현 및 테스트
5. workflow.py LangGraph 통합
6. CLI 인터페이스

### 💡 Low Priority (2주일 내)
7. 고급 기능 (에러 처리, 최적화)
8. 문서화
9. 추가 테스트

---

## 진행 상황 추적

**현재 단계**: ✅ Phase 2 완료 → Phase 3 준비 (LangGraph 워크플로우)

**다음 액션**: Phase 3 (LangGraph 워크플로우)
- workflow.py: State TypedDict 정의
- fetch_page_node, parse_and_convert_node 등 노드 구현
- Bedrock Claude 3.5 Sonnet 연동

**완료된 주요 기능**:
- ✅ Playwright 웹페이지 스크래핑 (자산 다운로드 포함)
- ✅ HTML → TSX 완전 변환 (20+ 단위 테스트)
- ✅ 중복 렌더링 문제 해결 (3가지 원인 모두 수정)
- ✅ AWS Bedrock을 이용한 HTML 유사도 검사
- ✅ 로컬 웹서버로 다운로드 HTML 테스트

**마지막 업데이트**: 2025-12-02

---

## 메모

- MVP는 단일 URL → React 컴포넌트 변환에 집중
- CSS/JS는 그대로 유지 (변환 X)
- 사람의 검토 및 개선 단계 필수
- 간단한 페이지부터 테스트 시작
