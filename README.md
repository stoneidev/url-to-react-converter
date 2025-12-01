# URL to React Converter

AWS Bedrock Claude를 활용한 웹페이지 자동 React 변환 시스템

## 프로젝트 개요

특정 URL의 웹페이지를 입력받아 React/Next.js 컴포넌트로 자동 변환하는 LangGraph 기반 Agentic AI

### 핵심 전략
- 페이지 단위 변환
- JavaScript/CSS는 그대로 유지
- HTML DOM → JSX 변환에 집중
- AWS Bedrock Claude Sonnet 4.5 사용

## 빠른 시작

### 사전 요구사항

1. **Python 3.10+**
2. **AWS CLI 설정**
3. **AWS Bedrock Claude 모델 액세스**

### 설치

```bash
# 1. Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Playwright 브라우저 설치
playwright install chromium

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 AWS 설정 확인
```

### AWS Bedrock 설정

```bash
# AWS 자격증명 확인
aws configure list

# Bedrock 모델 액세스 확인
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')]"

# 필요시 AWS Console에서 Model Access 활성화
# https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
```

## 사용법

```bash
# 기본 사용
python main.py https://example.com/pricing -n PricingPage

# 출력 디렉토리 지정
python main.py https://example.com/about -n AboutPage -o ./custom-output
```

## 프로젝트 구조

```
url-to-react-converter/
├── src/               # 소스 코드
│   ├── scraper.py     # Playwright 스크래핑
│   ├── converter.py   # HTML → JSX 변환
│   ├── workflow.py    # LangGraph 워크플로우
│   └── utils.py       # 유틸리티 함수
├── tests/             # 테스트 코드
├── templates/         # 프로젝트 템플릿
├── output/            # 생성된 컴포넌트 출력
├── examples/          # 예제 HTML 파일
├── requirements.txt   # Python 패키지
├── .env.example       # 환경 변수 템플릿
└── README.md
```

## 개발 상태

**현재**: Phase 1 완료 (프로젝트 설정)
**다음**: Phase 2 구현 (핵심 모듈)

자세한 내용은 `URL_TO_REACT_PROJECT.md` 참조

## 라이선스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!
