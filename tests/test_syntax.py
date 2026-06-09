"""Tests for syntax.py — tokenizer, comment splitter, token styles."""

import pytest
from syntax import (
    PYTHON_KEYWORDS,
    _TOKEN_RE,
    _token_style,
    _split_comment,
    KEYWORD_COLOR,
    STRING_COLOR,
    NUMBER_COLOR,
    CODE_GREEN,
    COMMENT_COLOR,
)


class TestTokenRe:
    def test_single_quoted_string(self):
        assert _TOKEN_RE.findall("'hello'") == ["'hello'"]

    def test_double_quoted_string(self):
        assert _TOKEN_RE.findall('"world"') == ['"world"']

    def test_integer_literal(self):
        assert "42" in _TOKEN_RE.findall("x = 42")

    def test_float_literal(self):
        assert "3.14" in _TOKEN_RE.findall("x = 3.14")

    def test_identifier(self):
        assert "my_var" in _TOKEN_RE.findall("my_var")

    def test_string_not_split_by_operator(self):
        # name="Mehdi" — the = should not swallow the opening quote
        tokens = _TOKEN_RE.findall('name="Mehdi"')
        assert '"Mehdi"' in tokens

    def test_single_quote_assignment(self):
        tokens = _TOKEN_RE.findall("s='hello'")
        assert "'hello'" in tokens

    def test_keyword_in_expression(self):
        tokens = _TOKEN_RE.findall("def foo(x):")
        assert "def" in tokens
        assert "foo" in tokens
        assert "x" in tokens

    def test_empty_string_returns_empty(self):
        assert _TOKEN_RE.findall("") == []

    def test_operators_captured(self):
        tokens = _TOKEN_RE.findall("a + b")
        assert "a" in tokens
        assert "b" in tokens
        assert " + " in tokens

    def test_none_as_string_not_swallowed(self):
        # 'None' as string literal keeps quote prefix intact
        tokens = _TOKEN_RE.findall("'None'")
        assert tokens == ["'None'"]
        assert tokens[0].startswith("'")

    def test_multitoken_code_line(self):
        tokens = _TOKEN_RE.findall("self.head = None")
        assert "self" in tokens
        assert "head" in tokens
        assert "None" in tokens


class TestTokenStyle:
    def test_single_quoted_string_color(self):
        color, bold = _token_style("'hello'")
        assert color == STRING_COLOR
        assert bold is False

    def test_double_quoted_string_color(self):
        color, bold = _token_style('"world"')
        assert color == STRING_COLOR
        assert bold is False

    def test_integer_literal_color(self):
        color, bold = _token_style("42")
        assert color == NUMBER_COLOR
        assert bold is False

    def test_float_literal_color(self):
        color, bold = _token_style("3.14")
        assert color == NUMBER_COLOR
        assert bold is False

    def test_keyword_def_is_bold_red(self):
        color, bold = _token_style("def")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_keyword_if_is_bold(self):
        color, bold = _token_style("if")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_keyword_return_is_bold(self):
        color, bold = _token_style("return")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_keyword_class_is_bold(self):
        color, bold = _token_style("class")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_keyword_None_is_bold(self):
        # None, True, False are in kwlist
        color, bold = _token_style("None")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_keyword_True_is_bold(self):
        color, bold = _token_style("True")
        assert color == KEYWORD_COLOR
        assert bold is True

    def test_identifier_is_code_green(self):
        color, bold = _token_style("my_var")
        assert color == CODE_GREEN
        assert bold is False

    def test_function_name_is_code_green(self):
        color, bold = _token_style("append")
        assert color == CODE_GREEN
        assert bold is False


class TestSplitComment:
    def test_no_comment_returns_full_line(self):
        code, comment = _split_comment("x = 1")
        assert code == "x = 1"
        assert comment == ""

    def test_simple_inline_comment(self):
        code, comment = _split_comment("x = 1  # a comment")
        assert "x = 1" in code
        assert comment == "# a comment"

    def test_hash_inside_single_quoted_string(self):
        code, comment = _split_comment("s = '#not_a_comment'")
        assert code == "s = '#not_a_comment'"
        assert comment == ""

    def test_hash_inside_double_quoted_string(self):
        code, comment = _split_comment('s = "#not_a_comment"')
        assert code == 's = "#not_a_comment"'
        assert comment == ""

    def test_comment_after_string_with_hash(self):
        code, comment = _split_comment("s = '#foo'  # real comment")
        assert comment == "# real comment"
        assert "'#foo'" in code

    def test_comment_only_line(self):
        code, comment = _split_comment("# just a comment")
        assert code == ""
        assert comment == "# just a comment"

    def test_empty_line(self):
        code, comment = _split_comment("")
        assert code == ""
        assert comment == ""

    def test_string_closes_before_comment(self):
        code, comment = _split_comment("print('hi')  # comment")
        assert comment == "# comment"

    def test_returns_tuple_of_two(self):
        result = _split_comment("x = 1")
        assert len(result) == 2


class TestPythonKeywords:
    def test_common_keywords_present(self):
        for kw in ["if", "else", "elif", "for", "while", "def", "class",
                   "return", "import", "from", "in", "not", "and", "or",
                   "True", "False", "None", "with", "as", "try", "except",
                   "finally", "raise", "pass", "break", "continue", "lambda"]:
            assert kw in PYTHON_KEYWORDS, f"{kw!r} should be a keyword"

    def test_non_keywords_absent(self):
        for word in ["foo", "my_var", "append", "data", "node", "print", "len"]:
            assert word not in PYTHON_KEYWORDS, f"{word!r} should not be a keyword"

    def test_is_frozenset(self):
        assert isinstance(PYTHON_KEYWORDS, frozenset)
