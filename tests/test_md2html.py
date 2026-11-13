from pathlib import Path

import pytest

from md2html import convert, inline
from build import build, get_title

FIXTURES = Path(__file__).parent / "fixtures"


# ---------- тесты на фикстурах: файл .md сравнивается с ожидаемым .html ----------

@pytest.mark.parametrize("name", ["headings", "lists", "code", "mixed"])
def test_fixture(name):
    source = (FIXTURES / (name + ".md")).read_text(encoding="utf-8")
    expected = (FIXTURES / (name + ".html")).read_text(encoding="utf-8")
    assert convert(source) == expected


# ---------- заголовки ----------

@pytest.mark.parametrize("level", [1, 2, 3, 4, 5, 6])
def test_heading_levels(level):
    assert convert("#" * level + " Тема") == f"<h{level}>Тема</h{level}>\n"


def test_seven_hashes_is_paragraph():
    assert convert("####### много") == "<p>####### много</p>\n"


def test_hash_without_space_is_paragraph():
    assert convert("#тег") == "<p>#тег</p>\n"


# ---------- списки ----------

def test_unordered_list():
    assert convert("- a\n- b") == "<ul>\n<li>a</li>\n<li>b</li>\n</ul>\n"


def test_ordered_list():
    assert convert("1. a\n2. b") == "<ol>\n<li>a</li>\n<li>b</li>\n</ol>\n"


def test_empty_line_splits_lists():
    assert convert("- a\n\n- b").count("<ul>") == 2


def test_list_is_closed_before_heading():
    assert convert("- a\n# Тема") == "<ul>\n<li>a</li>\n</ul>\n<h1>Тема</h1>\n"


# ---------- код ----------

def test_code_block_keeps_markdown_as_text():
    result = convert("```\n# не заголовок\n- не список\n```")
    assert result == "<pre><code># не заголовок\n- не список</code></pre>\n"


def test_code_block_escapes_html():
    assert "&lt;script&gt;" in convert("```\n<script>\n```")


def test_code_block_not_closed_still_rendered():
    # забыли закрыть ``` в конце файла
    assert convert("```\nx = 1") == "<pre><code>x = 1</code></pre>\n"


def test_inline_code():
    assert inline("вызов `f(x)` тут") == "вызов <code>f(x)</code> тут"


# ---------- абзацы и экранирование ----------

def test_empty_input():
    assert convert("") == ""


def test_lines_are_joined_into_one_paragraph():
    assert convert("первая\nвторая") == "<p>первая вторая</p>\n"


def test_html_is_escaped_in_text():
    assert convert("<b>жирный</b> & всё") == "<p>&lt;b&gt;жирный&lt;/b&gt; &amp; всё</p>\n"


# ---------- сборка сайта ----------

def test_get_title():
    assert get_title("текст\n# Лекция 5\n## дальше", "запасной") == "Лекция 5"
    assert get_title("нет заголовка", "запасной") == "запасной"


def test_build_creates_pages_and_index(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "a.md").write_text("# Первая\n\nтекст", encoding="utf-8")
    (notes / "b.md").write_text("- пункт", encoding="utf-8")
    out = tmp_path / "public"

    assert build(notes, out) == 2

    assert "<h1>Первая</h1>" in (out / "a.html").read_text(encoding="utf-8")
    index = (out / "index.html").read_text(encoding="utf-8")
    assert '<a href="a.html">Первая</a>' in index
    assert '<a href="b.html">b</a>' in index


def test_build_empty_folder(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    assert build(notes, tmp_path / "public") == 0
