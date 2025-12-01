"""
converter.py 단위 테스트
"""

import pytest
from src.converter import HTMLToJSXConverter


class TestHTMLToJSXConverter:
    """HTMLToJSXConverter 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행"""
        self.converter = HTMLToJSXConverter()

    def test_basic_conversion(self):
        """기본 HTML → JSX 변환"""
        html = '<div class="container"><p>Hello World</p></div>'
        jsx = self.converter.convert(html)

        assert 'className="container"' in jsx
        assert '<p>Hello World</p>' in jsx
        assert '<div' in jsx

    def test_class_to_classname(self):
        """class → className 변환"""
        html = '<div class="test-class">Content</div>'
        jsx = self.converter.convert(html)

        assert 'className=' in jsx
        assert 'class=' not in jsx or 'className=' in jsx

    def test_style_attribute(self):
        """style 속성 변환"""
        html = '<div style="color: red; font-size: 14px">Styled</div>'
        jsx = self.converter.convert(html)

        assert 'style={{' in jsx
        assert 'color' in jsx
        assert 'fontSize' in jsx

    def test_self_closing_tags(self):
        """Self-closing 태그 처리"""
        html = '<img src="test.jpg" alt="Test"><br><input type="text">'
        jsx = self.converter.convert(html)

        assert '<img' in jsx and '/>' in jsx
        assert '<br' in jsx and '/>' in jsx
        assert '<input' in jsx and '/>' in jsx

    def test_for_to_htmlfor(self):
        """for → htmlFor 변환"""
        html = '<label for="name">Name:</label>'
        jsx = self.converter.convert(html)

        assert 'htmlFor=' in jsx

    def test_boolean_attributes(self):
        """Boolean 속성 처리"""
        html = '<input type="checkbox" checked disabled>'
        jsx = self.converter.convert(html)

        assert 'checked' in jsx
        assert 'disabled' in jsx

    def test_data_attributes(self):
        """data-* 속성 유지"""
        html = '<div data-id="123" data-name="test">Content</div>'
        jsx = self.converter.convert(html)

        assert 'data-id' in jsx
        assert 'data-name' in jsx

    def test_aria_attributes(self):
        """aria-* 속성 유지"""
        html = '<button aria-label="Close" aria-hidden="true">X</button>'
        jsx = self.converter.convert(html)

        assert 'aria-label' in jsx
        assert 'aria-hidden' in jsx

    def test_nested_elements(self):
        """중첩된 요소 처리"""
        html = '''
        <div class="outer">
            <div class="inner">
                <p>Text</p>
            </div>
        </div>
        '''
        jsx = self.converter.convert(html)

        assert 'className="outer"' in jsx
        assert 'className="inner"' in jsx
        assert '<p>Text</p>' in jsx

    def test_empty_elements(self):
        """빈 요소 처리"""
        html = '<div></div>'
        jsx = self.converter.convert(html)

        assert '<div>' in jsx
        assert '</div>' in jsx

    def test_special_characters_in_text(self):
        """텍스트 내 특수 문자"""
        html = '<p>Price: $100 & up</p>'
        jsx = self.converter.convert(html)

        assert 'Price' in jsx
        assert '$100' in jsx

    def test_multiple_classes(self):
        """여러 클래스"""
        html = '<div class="class1 class2 class3">Content</div>'
        jsx = self.converter.convert(html)

        assert 'className="class1 class2 class3"' in jsx

    def test_inline_script_removal(self):
        """인라인 스크립트 제거"""
        html = '<script>alert("test")</script>'
        jsx = self.converter.convert(html)

        # 인라인 스크립트는 주석으로 변환되어야 함
        assert 'alert' not in jsx or '/*' in jsx

    def test_svg_attributes(self):
        """SVG 속성 변환"""
        html = '<svg><path stroke-width="2" fill-opacity="0.5"></path></svg>'
        jsx = self.converter.convert(html)

        assert 'strokeWidth' in jsx
        assert 'fillOpacity' in jsx

    def test_tabindex_conversion(self):
        """tabindex → tabIndex"""
        html = '<div tabindex="0">Focusable</div>'
        jsx = self.converter.convert(html)

        assert 'tabIndex' in jsx

    def test_readonly_conversion(self):
        """readonly → readOnly"""
        html = '<input type="text" readonly>'
        jsx = self.converter.convert(html)

        assert 'readOnly' in jsx

    def test_complex_html(self):
        """복잡한 HTML 구조"""
        html = '''
        <div class="container" style="padding: 20px">
            <header class="header">
                <h1>Title</h1>
                <nav>
                    <a href="/" class="active">Home</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            <main>
                <article>
                    <p>Content here</p>
                    <img src="image.jpg" alt="Image" />
                </article>
            </main>
        </div>
        '''
        jsx = self.converter.convert(html)

        assert 'className="container"' in jsx
        assert 'style={{' in jsx
        assert 'padding' in jsx
        assert '<header' in jsx
        assert '<nav>' in jsx
        assert '<main>' in jsx


def test_style_string_conversion():
    """스타일 문자열 변환 단독 테스트"""
    converter = HTMLToJSXConverter()

    style = "color: red; font-size: 14px; background-color: blue"
    result = converter._convert_style_string(style)

    assert 'color' in result
    assert 'fontSize' in result
    assert 'backgroundColor' in result


def test_camel_case_conversion():
    """kebab-case → camelCase 변환 테스트"""
    converter = HTMLToJSXConverter()

    assert converter._to_camel_case('font-size') == 'fontSize'
    assert converter._to_camel_case('background-color') == 'backgroundColor'
    assert converter._to_camel_case('border-top-width') == 'borderTopWidth'
    assert converter._to_camel_case('simple') == 'simple'


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
