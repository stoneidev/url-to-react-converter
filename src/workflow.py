"""
LangGraph 워크플로우
HTML을 분석하여 Next.js 구조(layout, page, components)로 변환
"""

from typing import TypedDict, List, Dict, Optional, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from bs4 import BeautifulSoup, Tag
import os
import subprocess
import shutil
from pathlib import Path

from .converter import HTMLToTSXConverter


class State(TypedDict):
    """워크플로우 상태"""
    # 입력
    html_path: str
    output_dir: str
    component_name: str
    assets_dir: str  # static 파일들이 있는 디렉토리
    create_project: bool  # Next.js 프로젝트 생성 여부

    # HTML 파싱 결과
    html_content: str
    soup: Optional[BeautifulSoup]

    # 추출된 요소들
    head_links: List[str]  # CSS 링크
    head_scripts: List[str]  # JS 스크립트
    meta_tags: List[str]  # meta 태그들
    body_html: str  # body 내용

    # 컴포넌트 분리 결과
    components: Annotated[List[Dict], operator.add]  # 분리된 컴포넌트들

    # 생성된 코드
    layout_code: str
    page_code: str

    # LLM 개선 결과
    enhanced_layout: str
    enhanced_page: str
    enhanced_components: List[Dict]

    # Next.js 프로젝트 정보
    nextjs_project_dir: str
    is_app_router: bool  # app router인지 pages router인지

    # 에러
    errors: Annotated[List[str], operator.add]


class HTMLToReactWorkflow:
    """HTML을 React 구조로 변환하는 워크플로우"""

    def __init__(self, bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        self.converter = HTMLToTSXConverter()
        self.llm = ChatBedrock(
            model_id=bedrock_model_id,
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={"max_tokens": 8192}  # 더 긴 출력 허용
        )

        # 워크플로우 그래프 생성
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """LangGraph 워크플로우 생성"""
        workflow = StateGraph(State)

        # 노드 추가
        workflow.add_node("load_html", self.load_html_node)
        workflow.add_node("parse_structure", self.parse_structure_node)
        workflow.add_node("extract_layout", self.extract_layout_node)
        workflow.add_node("identify_components", self.identify_components_node)
        workflow.add_node("convert_to_tsx", self.convert_to_tsx_node)
        workflow.add_node("enhance_with_llm", self.enhance_with_llm_node)
        workflow.add_node("setup_nextjs", self.setup_nextjs_project_node)
        workflow.add_node("copy_assets", self.copy_static_assets_node)
        workflow.add_node("deploy_files", self.deploy_files_node)

        # 엣지 설정 (순차적 실행)
        workflow.set_entry_point("load_html")
        workflow.add_edge("load_html", "parse_structure")
        workflow.add_edge("parse_structure", "extract_layout")
        workflow.add_edge("extract_layout", "identify_components")
        workflow.add_edge("identify_components", "convert_to_tsx")
        workflow.add_edge("convert_to_tsx", "enhance_with_llm")
        workflow.add_edge("enhance_with_llm", "setup_nextjs")
        workflow.add_edge("setup_nextjs", "copy_assets")
        workflow.add_edge("copy_assets", "deploy_files")
        workflow.add_edge("deploy_files", END)

        return workflow.compile()

    def load_html_node(self, state: State) -> State:
        """HTML 파일 로드"""
        print(f"\n📂 Loading HTML: {state['html_path']}")

        try:
            html_path = Path(state['html_path'])
            if not html_path.exists():
                state['errors'].append(f"HTML file not found: {state['html_path']}")
                return state

            html_content = html_path.read_text(encoding='utf-8')
            state['html_content'] = html_content
            state['soup'] = BeautifulSoup(html_content, 'html.parser')

            print(f"✅ HTML loaded successfully ({len(html_content)} bytes)")

        except Exception as e:
            state['errors'].append(f"Failed to load HTML: {str(e)}")

        return state

    def parse_structure_node(self, state: State) -> State:
        """HTML 구조 파싱"""
        print(f"\n🔍 Parsing HTML structure...")

        soup = state['soup']
        if not soup:
            state['errors'].append("No HTML content to parse")
            return state

        try:
            # <head> 요소들 추출
            head = soup.find('head')
            if head:
                # CSS 링크
                state['head_links'] = [
                    str(link) for link in head.find_all('link', rel='stylesheet')
                ]

                # JS 스크립트
                state['head_scripts'] = [
                    str(script) for script in head.find_all('script', src=True)
                ]

                # Meta 태그
                state['meta_tags'] = [
                    str(meta) for meta in head.find_all('meta')
                ]

            # <body> 내용
            body = soup.find('body')
            if body:
                state['body_html'] = str(body)
            else:
                # body가 없으면 전체를 사용
                state['body_html'] = str(soup)

            print(f"✅ Structure parsed:")
            print(f"   - CSS links: {len(state['head_links'])}")
            print(f"   - JS scripts: {len(state['head_scripts'])}")
            print(f"   - Meta tags: {len(state['meta_tags'])}")

        except Exception as e:
            state['errors'].append(f"Failed to parse structure: {str(e)}")

        return state

    def extract_layout_node(self, state: State) -> State:
        """Layout 코드 생성 (<head> 요소들)"""
        print(f"\n🏗️  Generating layout.tsx...")

        try:
            # CSS 링크들을 TSX로 변환
            css_links = '\n      '.join(state['head_links'])

            # JS 스크립트들을 TSX로 변환
            js_scripts = '\n      '.join(state['head_scripts'])

            # Meta 태그들을 TSX로 변환
            meta_tags = '\n      '.join(state['meta_tags'])

            # layout.tsx 템플릿
            layout_code = f'''export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="ko">
      <head>
        {meta_tags}
        {css_links}
        {js_scripts}
      </head>
      <body>{{children}}</body>
    </html>
  )
}}
'''

            state['layout_code'] = layout_code
            print(f"✅ Layout code generated")

        except Exception as e:
            state['errors'].append(f"Failed to generate layout: {str(e)}")

        return state

    def identify_components_node(self, state: State) -> State:
        """재사용 가능한 컴포넌트 식별"""
        print(f"\n🧩 Identifying reusable components...")

        try:
            soup = BeautifulSoup(state['body_html'], 'html.parser')
            components = []

            # 1. id 속성이 있는 주요 섹션들 (배너, 슬라이더 등)
            main_sections = soup.find_all(id=True)
            for section in main_sections:
                section_id = section.get('id', '')

                # 특정 패턴의 id를 가진 요소들을 컴포넌트로 추출
                if any(keyword in section_id for keyword in ['banner', 'slider', 'nav', 'header', 'footer', 'sidebar']):
                    component_name = self._id_to_component_name(section_id)
                    components.append({
                        'name': component_name,
                        'html': str(section),
                        'description': f"Component extracted from #{section_id}"
                    })

                    # 원본에서는 컴포넌트 호출로 대체
                    placeholder = soup.new_tag('div')
                    placeholder['data-component'] = component_name
                    section.replace_with(placeholder)

            # 2. 반복되는 구조 찾기 (class가 같은 형제 요소들)
            # TODO: 더 정교한 패턴 매칭 구현

            # 나머지 body 내용을 page.tsx로
            state['body_html'] = str(soup)

            if components:
                state['components'] = components
                print(f"✅ Found {len(components)} components:")
                for comp in components:
                    print(f"   - {comp['name']}")
            else:
                print(f"⚠️  No reusable components identified")

        except Exception as e:
            state['errors'].append(f"Failed to identify components: {str(e)}")

        return state

    def _id_to_component_name(self, element_id: str) -> str:
        """id를 PascalCase 컴포넌트 이름으로 변환"""
        # band_top_banner -> BandTopBanner
        parts = element_id.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in parts)

    def convert_to_tsx_node(self, state: State) -> State:
        """HTML을 TSX 문법으로 변환"""
        print(f"\n⚛️  Converting to TSX syntax...")

        try:
            # Body를 TSX로 변환
            body_tsx = self.converter.convert(state['body_html'])

            # placeholder를 컴포넌트 호출로 변경
            components = state.get('components', [])
            for component in components:
                component_name = component['name']
                # <div data-component="ComponentName"></div> -> <ComponentName />
                body_tsx = body_tsx.replace(
                    f'<div data-component="{component_name}"></div>',
                    f'<{component_name} />'
                )
                body_tsx = body_tsx.replace(
                    f'<div data-component="{component_name}" />',
                    f'<{component_name} />'
                )

            # import 문 생성
            import_statements = '\n'.join([
                f"import {comp['name']} from '@/components/{comp['name']}';"
                for comp in components
            ])

            # page.tsx 템플릿
            if import_statements:
                page_code = f'''{import_statements}

export default function {state['component_name']}() {{
  return (
    <>
      {body_tsx}
    </>
  )
}}
'''
            else:
                page_code = f'''export default function {state['component_name']}() {{
  return (
    <>
      {body_tsx}
    </>
  )
}}
'''

            state['page_code'] = page_code

            # 각 컴포넌트도 TSX로 변환
            for component in components:
                component_tsx = self.converter.convert(component['html'])
                component['tsx'] = f'''export default function {component['name']}() {{
  return (
    <>
      {component_tsx}
    </>
  )
}}
'''

            print(f"✅ Converted to TSX")

        except Exception as e:
            state['errors'].append(f"Failed to convert to TSX: {str(e)}")

        return state

    def _clean_llm_response(self, response: str) -> str:
        """LLM 응답에서 마크다운 코드 블록 제거"""
        # ```tsx 또는 ```typescript 또는 ``` 제거
        response = response.strip()

        # 시작 코드 블록 제거
        if response.startswith('```tsx'):
            response = response[6:].lstrip()
        elif response.startswith('```typescript'):
            response = response[13:].lstrip()
        elif response.startswith('```'):
            response = response[3:].lstrip()

        # 끝 코드 블록 제거
        if response.endswith('```'):
            response = response[:-3].rstrip()

        return response

    def enhance_with_llm_node(self, state: State) -> State:
        """LLM으로 코드 개선"""
        print(f"\n✨ Enhancing code with Claude 3.5 Sonnet...")

        try:
            # Layout 개선
            layout_prompt = f"""다음 React layout.tsx 코드를 개선해주세요:

{state['layout_code']}

개선 사항:
1. 필요한 import 문 추가 (React 등)
2. TypeScript 타입 정확히 지정
3. meta 태그 중복 제거
4. 불필요한 요소 제거
5. 코드 포맷팅

개선된 코드만 반환하고 설명은 생략해주세요. 마크다운 코드 블록(```tsx)을 사용하지 말고 순수 코드만 반환해주세요."""

            layout_response = self.llm.invoke(layout_prompt)
            state['enhanced_layout'] = self._clean_llm_response(layout_response.content)

            # Page 개선
            page_prompt = f"""다음 React page.tsx 코드를 개선해주세요:

{state['page_code']}

개선 사항:
1. 기존의 컴포넌트 import 문은 반드시 유지
2. 필요한 추가 import 문 추가 (React 등)
3. 인라인 이벤트 핸들러를 함수로 추출
4. 반복되는 요소는 .map()으로 변환
5. key props 추가
6. 코드 포맷팅

중요: 코드 상단에 있는 컴포넌트 import 문들(import ComponentName from '@/components/ComponentName')은 절대 제거하지 말고 유지해주세요.
개선된 코드만 반환하고 설명은 생략해주세요. 마크다운 코드 블록(```tsx)을 사용하지 말고 순수 코드만 반환해주세요."""

            page_response = self.llm.invoke(page_prompt)
            state['enhanced_page'] = self._clean_llm_response(page_response.content)

            # Components 개선
            enhanced_components = []
            for component in state.get('components', []):
                comp_prompt = f"""다음 React 컴포넌트를 개선해주세요:

{component['tsx']}

개선 사항:
1. 필요한 import 문 추가
2. Props 타입 정의 (필요시)
3. 코드 포맷팅

개선된 코드만 반환하고 설명은 생략해주세요. 마크다운 코드 블록(```tsx)을 사용하지 말고 순수 코드만 반환해주세요."""

                comp_response = self.llm.invoke(comp_prompt)
                enhanced_components.append({
                    'name': component['name'],
                    'code': self._clean_llm_response(comp_response.content),
                    'description': component['description']
                })

            state['enhanced_components'] = enhanced_components

            print(f"✅ Code enhanced with LLM")

        except Exception as e:
            state['errors'].append(f"Failed to enhance with LLM: {str(e)}")
            # LLM 실패시 원본 사용
            state['enhanced_layout'] = state['layout_code']
            state['enhanced_page'] = state['page_code']
            state['enhanced_components'] = [
                {'name': c['name'], 'code': c.get('tsx', ''), 'description': c['description']}
                for c in state.get('components', [])
            ]

        return state

    def setup_nextjs_project_node(self, state: State) -> State:
        """Next.js 프로젝트 생성 또는 확인"""
        print(f"\n🏗️  Setting up Next.js project...")

        try:
            project_dir = Path(state['nextjs_project_dir'])

            # 프로젝트가 이미 존재하는지 확인
            if project_dir.exists():
                print(f"✅ Next.js project already exists: {project_dir}")

                # app router인지 pages router인지 확인
                app_dir = project_dir / "app"
                pages_dir = project_dir / "pages"

                if app_dir.exists():
                    state['is_app_router'] = True
                    print(f"   📁 Detected: App Router structure")
                elif pages_dir.exists():
                    state['is_app_router'] = False
                    print(f"   📁 Detected: Pages Router structure")
                else:
                    # 구조를 알 수 없으면 app router로 간주
                    state['is_app_router'] = True
                    print(f"   ⚠️  Unknown structure, defaulting to App Router")

            elif state['create_project']:
                # 새 프로젝트 생성
                print(f"🚀 Creating new Next.js project: {project_dir}")

                # npx create-next-app 실행
                cmd = [
                    "npx",
                    "--yes",  # 자동으로 yes 응답
                    "create-next-app@latest",
                    str(project_dir.name),
                    "--typescript",
                    "--tailwind",
                    "--eslint",
                    "--app",  # app router 사용
                    "--no-src-dir",
                    "--import-alias", "@/*",
                    "--use-npm"
                ]

                # 부모 디렉토리에서 실행
                parent_dir = project_dir.parent
                parent_dir.mkdir(parents=True, exist_ok=True)

                result = subprocess.run(
                    cmd,
                    cwd=parent_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print(f"✅ Next.js project created successfully!")
                    state['is_app_router'] = True
                else:
                    error_msg = f"Failed to create Next.js project: {result.stderr}"
                    state['errors'].append(error_msg)
                    print(f"❌ {error_msg}")

            else:
                error_msg = f"Project directory does not exist and create_project=False: {project_dir}"
                state['errors'].append(error_msg)
                print(f"❌ {error_msg}")

        except Exception as e:
            state['errors'].append(f"Failed to setup Next.js project: {str(e)}")

        return state

    def copy_static_assets_node(self, state: State) -> State:
        """static 파일들을 Next.js 프로젝트로 복사"""
        print(f"\n📦 Copying static assets...")

        try:
            project_dir = Path(state['nextjs_project_dir'])
            assets_src = Path(state['assets_dir'])

            if not assets_src.exists():
                print(f"⚠️  Assets directory not found: {assets_src}")
                return state

            # Next.js public 디렉토리에 복사
            public_dir = project_dir / "public"
            public_dir.mkdir(exist_ok=True)

            # assets 디렉토리 복사
            assets_dest = public_dir / "assets"
            if assets_dest.exists():
                shutil.rmtree(assets_dest)

            shutil.copytree(assets_src, assets_dest)
            print(f"✅ Copied assets to: {assets_dest}")

            # CSS/JS/images 개수 확인
            css_files = list(assets_dest.rglob("*.css"))
            js_files = list(assets_dest.rglob("*.js"))
            image_files = list(assets_dest.rglob("*.{png,jpg,jpeg,gif,svg,webp,ico}"))

            print(f"   - CSS files: {len(css_files)}")
            print(f"   - JS files: {len(js_files)}")
            print(f"   - Images: {len(image_files)}")

        except Exception as e:
            state['errors'].append(f"Failed to copy assets: {str(e)}")

        return state

    def deploy_files_node(self, state: State) -> State:
        """생성된 TSX 파일들을 Next.js 프로젝트에 배치"""
        print(f"\n🚀 Deploying TSX files to Next.js project...")

        try:
            project_dir = Path(state['nextjs_project_dir'])

            if state['is_app_router']:
                # App Router 구조
                app_dir = project_dir / "app"
                app_dir.mkdir(exist_ok=True)

                # layout.tsx 배치
                layout_path = app_dir / "layout.tsx"
                layout_path.write_text(state['enhanced_layout'], encoding='utf-8')
                print(f"✅ Deployed: {layout_path}")

                # page.tsx 배치
                page_path = app_dir / "page.tsx"
                page_path.write_text(state['enhanced_page'], encoding='utf-8')
                print(f"✅ Deployed: {page_path}")

                # components 배치
                if state.get('enhanced_components'):
                    components_dir = project_dir / "components"
                    components_dir.mkdir(exist_ok=True)

                    for component in state['enhanced_components']:
                        comp_path = components_dir / f"{component['name']}.tsx"
                        comp_path.write_text(component['code'], encoding='utf-8')
                        print(f"✅ Deployed: {comp_path}")

            else:
                # Pages Router 구조
                pages_dir = project_dir / "pages"
                pages_dir.mkdir(exist_ok=True)

                # _app.tsx에 layout 통합 (간단히 page만 생성)
                page_path = pages_dir / "index.tsx"
                page_path.write_text(state['enhanced_page'], encoding='utf-8')
                print(f"✅ Deployed: {page_path}")

                # components 배치
                if state.get('enhanced_components'):
                    components_dir = project_dir / "components"
                    components_dir.mkdir(exist_ok=True)

                    for component in state['enhanced_components']:
                        comp_path = components_dir / f"{component['name']}.tsx"
                        comp_path.write_text(component['code'], encoding='utf-8')
                        print(f"✅ Deployed: {comp_path}")

            print(f"\n🎉 All files deployed successfully!")
            print(f"\n📂 Project location: {project_dir}")
            print(f"\n💡 Next steps:")
            print(f"   cd {project_dir}")
            print(f"   npm install")
            print(f"   npm run dev")

        except Exception as e:
            state['errors'].append(f"Failed to deploy files: {str(e)}")

        return state

    def run(
        self,
        html_path: str,
        nextjs_project_dir: str = "./output/nextjs-app",
        component_name: str = "HomePage",
        assets_dir: str = "./output/assets",
        create_project: bool = True
    ) -> State:
        """워크플로우 실행"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting HTML to Next.js conversion workflow")
        print(f"{'='*60}")

        initial_state: State = {
            'html_path': html_path,
            'output_dir': nextjs_project_dir,  # 호환성을 위해 유지
            'component_name': component_name,
            'assets_dir': assets_dir,
            'create_project': create_project,
            'nextjs_project_dir': nextjs_project_dir,
            'is_app_router': True,
            'html_content': '',
            'soup': None,
            'head_links': [],
            'head_scripts': [],
            'meta_tags': [],
            'body_html': '',
            'components': [],
            'layout_code': '',
            'page_code': '',
            'enhanced_layout': '',
            'enhanced_page': '',
            'enhanced_components': [],
            'errors': []
        }

        # 워크플로우 실행
        final_state = self.workflow.invoke(initial_state)

        # 결과 출력
        print(f"\n{'='*60}")
        if final_state['errors']:
            print(f"⚠️  Completed with errors:")
            for error in final_state['errors']:
                print(f"   - {error}")
        else:
            print(f"✅ Conversion completed successfully!")
        print(f"{'='*60}")

        return final_state


def main():
    """CLI 실행"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Convert HTML to Next.js project")
    parser.add_argument("html_file", help="Path to HTML file")
    parser.add_argument("--project-dir", default="./output/nextjs-app", help="Next.js project directory")
    parser.add_argument("--component-name", default="HomePage", help="Main component name")
    parser.add_argument("--assets-dir", default="./output/assets", help="Assets directory")
    parser.add_argument("--no-create", action="store_true", help="Don't create new project (use existing)")

    args = parser.parse_args()

    workflow = HTMLToReactWorkflow()
    workflow.run(
        html_path=args.html_file,
        nextjs_project_dir=args.project_dir,
        component_name=args.component_name,
        assets_dir=args.assets_dir,
        create_project=not args.no_create
    )


if __name__ == "__main__":
    main()
