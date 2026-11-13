"""Собирает сайт с заметками: notes/*.md -> public/*.html + index.html."""
import html
import sys
from pathlib import Path

from md2html import convert

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: sans-serif; max-width: 760px; margin: 2em auto; padding: 0 1em; line-height: 1.5; }}
pre {{ background: #f4f4f4; padding: 1em; overflow-x: auto; }}
code {{ background: #f4f4f4; padding: 0 0.2em; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def get_title(markdown_text, default):
    """Заголовок страницы = первый заголовок первого уровня в заметке."""
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return default


def build(notes_dir, out_dir):
    notes_dir = Path(notes_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    links = []
    for md_file in sorted(notes_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        title = get_title(text, md_file.stem)
        body = convert(text) + '<p><a href="index.html">К списку заметок</a></p>'
        out_file = out_dir / (md_file.stem + ".html")
        out_file.write_text(PAGE.format(title=html.escape(title), body=body), encoding="utf-8")
        links.append((out_file.name, title))
        print("собрано:", md_file.name, "->", out_file)

    items = "\n".join(f'<li><a href="{name}">{html.escape(title)}</a></li>' for name, title in links)
    index_body = "<h1>Заметки лекций</h1>\n<ul>\n" + items + "\n</ul>"
    (out_dir / "index.html").write_text(PAGE.format(title="Заметки лекций", body=index_body), encoding="utf-8")
    print("всего заметок:", len(links))
    return len(links)


if __name__ == "__main__":
    count = build("notes", "public")
    if count == 0:
        print("в папке notes нет заметок")
        sys.exit(1)
