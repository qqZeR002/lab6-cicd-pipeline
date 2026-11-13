"""Упрощённый конвертер Markdown -> HTML для заметок лекций.

Поддерживается только подмножество Markdown:
  - заголовки #, ##, ... ######
  - маркированные списки (- или *) и нумерованные (1. 2. ...)
  - блоки кода в тройных обратных кавычках и `код в строке`
  - обычные абзацы
"""
import html
import re

HEADING_RE = re.compile(r"^(#{1,7})\s+(.+)$")
UL_RE = re.compile(r"^[-*]\s+(.+)$")
OL_RE = re.compile(r"^\d+\.\s+(.+)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def inline(text):
    """Экранирует спецсимволы HTML и заменяет `код` на <code>."""
    text = html.escape(text, quote=False)
    return INLINE_CODE_RE.sub(r"<code>\1</code>", text)


def convert(markdown_text):
    """Превращает текст Markdown в строку HTML."""
    result = []
    paragraph = []      # строки текущего абзаца
    list_tag = None     # "ul", "ol" или None, если списка сейчас нет
    in_code = False
    code_lines = []

    def close_paragraph():
        if paragraph:
            result.append("<p>" + " ".join(paragraph) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_tag
        if list_tag:
            result.append("</" + list_tag + ">")
            list_tag = None

    for line in markdown_text.splitlines():
        # --- блок кода ---
        if line.strip().startswith("```"):
            if in_code:
                code = html.escape("\n".join(code_lines), quote=False)
                result.append("<pre><code>" + code + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_paragraph()
                close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)   # внутри кода ничего не разбираем
            continue

        stripped = line.strip()

        # --- пустая строка закрывает абзац и список ---
        if stripped == "":
            close_paragraph()
            close_list()
            continue

        # --- заголовок ---
        m = HEADING_RE.match(stripped)
        if m:
            close_paragraph()
            close_list()
            level = len(m.group(1))
            result.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            continue

        # --- списки ---
        m_ul = UL_RE.match(stripped)
        m_ol = OL_RE.match(stripped)
        if m_ul or m_ol:
            new_tag = "ul" if m_ul else "ol"
            item = (m_ul or m_ol).group(1)
            close_paragraph()
            if list_tag != new_tag:
                close_list()
                result.append("<" + new_tag + ">")
                list_tag = new_tag
            result.append("<li>" + inline(item) + "</li>")
            continue

        # --- обычный текст ---
        close_list()
        paragraph.append(inline(stripped))

    # конец файла: закрываем всё, что осталось открытым
    if in_code:
        code = html.escape("\n".join(code_lines), quote=False)
        result.append("<pre><code>" + code + "</code></pre>")
    close_paragraph()
    close_list()

    return "\n".join(result) + ("\n" if result else "")
