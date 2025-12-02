"""
converter.py 단위 테스트
"""

import pytest
from src.converter import HTMLToTSXConverter


class TestHTMLToTSXConverter:
    """HTMLToTSXConverter 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행"""
        self.converter = HTMLToTSXConverter()

    def test_basic_conversion(self):
        """기본 HTML → TSX 변환"""
        html = '<div class="container"><p>Hello World</p></div>'
        tsx = self.converter.convert(html)

        assert 'className="container"' in tsx
        assert '<p>Hello World</p>' in tsx
        assert '<div' in tsx

    def test_class_to_classname(self):
        """class → className 변환"""
        html = '<div class="test-class">Content</div>'
        tsx = self.converter.convert(html)

        assert 'className=' in tsx
        assert 'class=' not in tsx or 'className=' in tsx

    def test_style_attribute(self):
        """style 속성 변환"""
        html = '<div style="color: red; font-size: 14px">Styled</div>'
        tsx = self.converter.convert(html)

        assert 'style={{' in tsx
        assert 'color' in tsx
        assert 'fontSize' in tsx

    def test_self_closing_tags(self):
        """Self-closing 태그 처리"""
        html = '<img src="test.jpg" alt="Test"><br><input type="text">'
        tsx = self.converter.convert(html)

        assert '<img' in tsx and '/>' in tsx
        assert '<br' in tsx and '/>' in tsx
        assert '<input' in tsx and '/>' in tsx

    def test_for_to_htmlfor(self):
        """for → htmlFor 변환"""
        html = '<label for="name">Name:</label>'
        tsx = self.converter.convert(html)

        assert 'htmlFor=' in tsx

    def test_boolean_attributes(self):
        """Boolean 속성 처리"""
        html = '<input type="checkbox" checked disabled>'
        tsx = self.converter.convert(html)

        assert 'checked' in tsx
        assert 'disabled' in tsx

    def test_data_attributes(self):
        """data-* 속성 유지"""
        html = '<div data-id="123" data-name="test">Content</div>'
        tsx = self.converter.convert(html)

        assert 'data-id' in tsx
        assert 'data-name' in tsx

    def test_aria_attributes(self):
        """aria-* 속성 유지"""
        html = '<button aria-label="Close" aria-hidden="true">X</button>'
        tsx = self.converter.convert(html)

        assert 'aria-label' in tsx
        assert 'aria-hidden' in tsx

    def test_nested_elements(self):
        """중첩된 요소 처리"""
        html = '''
        <div class="outer">
            <div class="inner">
                <p>Text</p>
            </div>
        </div>
        '''
        tsx = self.converter.convert(html)

        assert 'className="outer"' in tsx
        assert 'className="inner"' in tsx
        assert '<p>Text</p>' in tsx

    def test_empty_elements(self):
        """빈 요소 처리"""
        html = '<div></div>'
        tsx = self.converter.convert(html)

        assert '<div>' in tsx
        assert '</div>' in tsx

    def test_special_characters_in_text(self):
        """텍스트 내 특수 문자"""
        html = '<p>Price: $100 & up</p>'
        tsx = self.converter.convert(html)

        assert 'Price' in tsx
        assert '$100' in tsx

    def test_multiple_classes(self):
        """여러 클래스"""
        html = '<div class="class1 class2 class3">Content</div>'
        tsx = self.converter.convert(html)

        assert 'className="class1 class2 class3"' in tsx

    def test_inline_script_removal(self):
        """인라인 스크립트 제거"""
        html = '<script>alert("test")</script>'
        tsx = self.converter.convert(html)

        # 인라인 스크립트는 주석으로 변환되어야 함
        assert 'alert' not in tsx or '/*' in tsx

    def test_svg_attributes(self):
        """SVG 속성 변환"""
        html = '<svg><path stroke-width="2" fill-opacity="0.5"></path></svg>'
        tsx = self.converter.convert(html)

        assert 'strokeWidth' in tsx
        assert 'fillOpacity' in tsx

    def test_tabindex_conversion(self):
        """tabindex → tabIndex"""
        html = '<div tabindex="0">Focusable</div>'
        tsx = self.converter.convert(html)

        assert 'tabIndex' in tsx

    def test_readonly_conversion(self):
        """readonly → readOnly"""
        html = '<input type="text" readonly>'
        tsx = self.converter.convert(html)

        assert 'readOnly' in tsx

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
        tsx = self.converter.convert(html)

        assert 'className="container"' in tsx
        assert 'style={{' in tsx
        assert 'padding' in tsx
        assert '<header' in tsx
        assert '<nav>' in tsx
        assert '<main>' in tsx


def test_style_string_conversion():
    """스타일 문자열 변환 단독 테스트"""
    converter = HTMLToTSXConverter()

    style = "color: red; font-size: 14px; background-color: blue"
    result = converter._convert_style_string(style)

    assert 'color' in result
    assert 'fontSize' in result
    assert 'backgroundColor' in result


def test_camel_case_conversion():
    """kebab-case → camelCase 변환 테스트"""
    converter = HTMLToTSXConverter()

    assert converter._to_camel_case('font-size') == 'fontSize'
    assert converter._to_camel_case('background-color') == 'backgroundColor'
    assert converter._to_camel_case('border-top-width') == 'borderTopWidth'
    assert converter._to_camel_case('simple') == 'simple'


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
