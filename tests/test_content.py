"""Tests for content.py — validates the SECTIONS data structure."""

import pytest


@pytest.fixture(scope="module")
def sections():
    from content import SECTIONS
    return SECTIONS


class TestSectionsStructure:
    def test_is_a_list(self, sections):
        assert isinstance(sections, list)

    def test_not_empty(self, sections):
        assert len(sections) > 0

    def test_first_section_is_title_type(self, sections):
        assert sections[0]["type"] == "title"

    def test_all_sections_have_type(self, sections):
        for s in sections:
            assert "type" in s, f"section {s} missing 'type'"

    def test_all_sections_have_heading(self, sections):
        for s in sections:
            assert "heading" in s, f"section {s} missing 'heading'"

    def test_all_sections_have_on_screen_text(self, sections):
        for s in sections:
            assert "on_screen_text" in s, f"section {s} missing 'on_screen_text'"

    def test_all_types_are_valid(self, sections):
        valid = {"title", "text", "code"}
        for s in sections:
            assert s["type"] in valid, f"unknown type {s['type']!r}"

    def test_title_section_has_duration_when_no_narration(self, sections):
        for s in sections:
            if s["type"] == "title" and not s.get("narration"):
                assert "duration" in s
                assert s["duration"] > 0

    def test_code_sections_have_body(self, sections):
        for s in sections:
            if s["type"] == "code":
                assert "body" in s
                assert len(s["body"]) > 0

    def test_text_sections_have_body(self, sections):
        for s in sections:
            if s["type"] == "text":
                assert "body" in s

    def test_narrated_sections_have_nonempty_narration(self, sections):
        for s in sections:
            if s.get("narration"):
                assert s["narration"].strip(), f"section {s['heading']!r} has blank narration"

    def test_at_least_one_code_section(self, sections):
        assert any(s["type"] == "code" for s in sections)

    def test_at_least_one_text_section(self, sections):
        assert any(s["type"] == "text" for s in sections)

    def test_headings_are_nonempty_strings(self, sections):
        for s in sections:
            assert isinstance(s["heading"], str)
            assert s["heading"].strip()

    def test_on_screen_text_are_strings(self, sections):
        for s in sections:
            assert isinstance(s["on_screen_text"], str)

    def test_code_body_is_string(self, sections):
        for s in sections:
            if s["type"] == "code":
                assert isinstance(s["body"], str)
