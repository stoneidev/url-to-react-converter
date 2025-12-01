"""
HTML to JSX 변환 모듈
HTML 요소를 React JSX 문법으로 변환
"""

from typing import Union, Dict, List
from bs4 import BeautifulSoup, NavigableString, Tag, Comment


class HTMLToJSXConverter:
    """HTML을 JSX로 변환하는 클래스"""

    # HTML 속성 -> JSX 속성 매핑
    ATTR_MAP = {
        'class': 'className',
        'for': 'htmlFor',
        'tabindex': 'tabIndex',
        'readonly': 'readOnly',
        'maxlength': 'maxLength',
        'minlength': 'minLength',
        'cellpadding': 'cellPadding',
        'cellspacing': 'cellSpacing',
        'rowspan': 'rowSpan',
        'colspan': 'colSpan',
        'usemap': 'useMap',
        'frameborder': 'frameBorder',
        'contenteditable': 'contentEditable',
        'crossorigin': 'crossOrigin',
        'datetime': 'dateTime',
        'hreflang': 'hrefLang',
        'http-equiv': 'httpEquiv',
        'accept-charset': 'acceptCharset',
        'accesskey': 'accessKey',
        'autofocus': 'autoFocus',
        'autoplay': 'autoPlay',
        'charset': 'charSet',
        'formaction': 'formAction',
        'formenctype': 'formEncType',
        'formmethod': 'formMethod',
        'formnovalidate': 'formNoValidate',
        'formtarget': 'formTarget',
        'novalidate': 'noValidate',
        'spellcheck': 'spellCheck',
        'srcset': 'srcSet',
    }

    # SVG 속성 매핑 (kebab-case -> camelCase)
    SVG_ATTR_MAP = {
        'stroke-width': 'strokeWidth',
        'stroke-linecap': 'strokeLinecap',
        'stroke-linejoin': 'strokeLinejoin',
        'stroke-dasharray': 'strokeDasharray',
        'stroke-dashoffset': 'strokeDashoffset',
        'fill-opacity': 'fillOpacity',
        'fill-rule': 'fillRule',
        'clip-path': 'clipPath',
        'clip-rule': 'clipRule',
        'stop-color': 'stopColor',
        'stop-opacity': 'stopOpacity',
    }

    # Self-closing 태그 (void elements)
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr',
        'img', 'input', 'link', 'meta', 'param',
        'source', 'track', 'wbr', 'command', 'keygen'
    }

    def __init__(self):
        self.errors: List[str] = []

    def convert(self, html: str) -> str:
        """
        HTML 문자열을 JSX로 변환

        Args:
            html: HTML 문자열

        Returns:
            JSX 문자열
        """
        soup = BeautifulSoup(html, 'html.parser')

        # body 내용만 변환 (일반적으로 React 컴포넌트는 body 내용만 필요)
        body = soup.body
        if not body:
            # body가 없으면 전체 변환
            return self._convert_children(soup)

        return self._convert_children(body)

    def _convert_element(self, element: Union[Tag, NavigableString]) -> str:
        """단일 요소를 JSX로 변환"""

        # 텍스트 노드
        if isinstance(element, NavigableString):
            if isinstance(element, Comment):
                return f"{{/* {element} */}}"
            return self._escape_text(str(element))

        # HTML 태그
        if isinstance(element, Tag):
            tag_name = element.name

            # script와 style 태그는 특별 처리
            if tag_name == 'script':
                return self._convert_script(element)
            if tag_name == 'style':
                return self._convert_style(element)

            # 속성 변환
            attrs = self._convert_attributes(element.attrs, tag_name)

            # Self-closing 태그
            if tag_name in self.VOID_ELEMENTS and not element.contents:
                return f"<{tag_name}{attrs} />"

            # 일반 태그
            children = self._convert_children(element)
            return f"<{tag_name}{attrs}>{children}</{tag_name}>"

        return ""

    def _convert_children(self, element) -> str:
        """자식 요소들을 변환"""
        result = []
        for child in element.children:
            converted = self._convert_element(child)
            if converted:
                result.append(converted)
        return ''.join(result)

    def _convert_attributes(self, attrs: Dict, tag_name: str) -> str:
        """HTML 속성을 JSX 속성으로 변환"""
        if not attrs:
            return ""

        jsx_attrs = []

        for key, value in attrs.items():
            # 속성명 변환
            jsx_key = self._convert_attribute_name(key, tag_name)

            # 특수 처리: style 속성
            if jsx_key == 'style' and isinstance(value, str):
                style_obj = self._convert_style_string(value)
                if style_obj:
                    jsx_attrs.append(f'{jsx_key}={{{style_obj}}}')
                continue

            # Boolean 속성 (값이 없거나 키와 같음)
            if value is True or value == '' or value == key:
                jsx_attrs.append(jsx_key)
                continue

            # None이나 False는 생략
            if value is None or value is False:
                continue

            # 배열 값 (class 등)
            if isinstance(value, list):
                value_str = ' '.join(str(v) for v in value)
                jsx_attrs.append(f'{jsx_key}="{value_str}"')
                continue

            # 일반 문자열 값
            value_str = str(value).replace('"', '&quot;')
            jsx_attrs.append(f'{jsx_key}="{value_str}"')

        return ' ' + ' '.join(jsx_attrs) if jsx_attrs else ''

    def _convert_attribute_name(self, name: str, tag_name: str) -> str:
        """속성명 변환 (HTML -> JSX)"""
        # 소문자로 변환
        name_lower = name.lower()

        # SVG 요소의 경우 SVG 속성 매핑 우선
        if tag_name in ['svg', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon']:
            if name_lower in self.SVG_ATTR_MAP:
                return self.SVG_ATTR_MAP[name_lower]

        # 일반 HTML 속성 매핑
        if name_lower in self.ATTR_MAP:
            return self.ATTR_MAP[name_lower]

        # data-* 와 aria-* 속성은 그대로 유지
        if name_lower.startswith('data-') or name_lower.startswith('aria-'):
            return name_lower

        # 기타: kebab-case -> camelCase 변환
        if '-' in name_lower:
            return self._to_camel_case(name_lower)

        return name_lower

    def _convert_style_string(self, style_str: str) -> str:
        """
        style 문자열을 JSX 스타일 객체로 변환

        예: "color: red; font-size: 14px"
        -> {{color: 'red', fontSize: '14px'}}
        """
        if not style_str or not style_str.strip():
            return ""

        style_obj = {}

        for rule in style_str.split(';'):
            rule = rule.strip()
            if not rule or ':' not in rule:
                continue

            prop, val = rule.split(':', 1)
            prop = prop.strip()
            val = val.strip()

            if not prop or not val:
                continue

            # CSS 속성명을 camelCase로 변환
            prop_camel = self._to_camel_case(prop)

            # 값 이스케이핑
            val_escaped = val.replace("'", "\\'")

            style_obj[prop_camel] = val_escaped

        if not style_obj:
            return ""

        # 객체를 문자열로 변환
        items = [f"{k}: '{v}'" for k, v in style_obj.items()]
        return '{' + ', '.join(items) + '}'

    def _to_camel_case(self, kebab: str) -> str:
        """kebab-case를 camelCase로 변환"""
        parts = kebab.split('-')
        if len(parts) == 1:
            return parts[0]
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def _escape_text(self, text: str) -> str:
        """JSX 텍스트 이스케이핑"""
        # 공백만 있는 텍스트는 생략
        if not text.strip():
            return text

        # JSX에서 특수 문자 처리
        text = text.replace('{', '&#123;')
        text = text.replace('}', '&#125;')

        return text

    def _convert_script(self, element: Tag) -> str:
        """<script> 태그 처리"""
        # src 속성이 있으면 외부 스크립트
        if element.get('src'):
            attrs = self._convert_attributes(element.attrs, 'script')
            return f"<script{attrs}></script>"

        # 인라인 스크립트는 dangerouslySetInnerHTML 사용
        script_content = element.string or ''
        if script_content.strip():
            # 스크립트 내용을 주석으로 경고
            return f"{{/* Inline script removed - original content:\n{script_content}\n*/}}"

        return ""

    def _convert_style(self, element: Tag) -> str:
        """<style> 태그 처리"""
        # 인라인 스타일은 별도 CSS 파일로 추출 권장
        style_content = element.string or ''
        if style_content.strip():
            return f"{{/* Inline styles - consider moving to CSS file:\n{style_content}\n*/}}"

        return ""


def main():
    """CLI 테스트용"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python converter.py <html_file>")
        sys.exit(1)

    html_file = sys.argv[1]
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    converter = HTMLToJSXConverter()
    jsx = converter.convert(html)

    print(jsx)


if __name__ == "__main__":
    main()
