#!/usr/bin/env python3
"""Build static course and lesson navigation from the folders beside this file."""

import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SCRIPT_BLOCK = re.compile(rb"(<script\b[^>]*>)(.*?)(</script\s*>)", re.I | re.S)


def prepare_lesson(path):
    """Keep Live Server from injecting into a body-closing string in JavaScript."""
    original = path.read_bytes()

    def escape_body_string(match):
        # Escaping the slash preserves the JavaScript string's runtime value.
        script = re.sub(rb"</body>", lambda tag: b"<\\/" + tag[0][2:],
                        match[2], flags=re.I)
        return match[1] + script + match[3]

    prepared = SCRIPT_BLOCK.sub(escape_body_string, original)
    if prepared != original:
        path.write_bytes(prepared)
        return True
    return False


def natural_key(path):
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r"(\d+)", path.name)]


def label(name):
    return name.replace("-", " ")


def page(title, content, *, in_course=False):
    home = "../" if in_course else "./"
    stylesheet = "../navigation.css" if in_course else "navigation.css"
    breadcrumb = (f'<a href="../">All courses</a><span aria-hidden="true">/</span>'
                  f'<span>{html.escape(title)}</span>') if in_course else "All courses"
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · MD Courses</title>
  <link rel="stylesheet" href="{stylesheet}">
</head>
<body>
  <header class="site-header"><a class="brand" href="{home}"><span class="brand-mark">MD</span> Course library</a></header>
  <main>
    <nav class="breadcrumb" aria-label="Breadcrumb">{breadcrumb}</nav>
    {content}
  </main>
  <footer>MD Courses <span aria-hidden="true">·</span> Learn at your own pace</footer>
</body>
</html>
'''


def build():
    folders = sorted((path for path in ROOT.iterdir()
                      if path.is_dir() and not path.name.startswith(".")
                      and path.name not in {"__pycache__", "node_modules"}), key=natural_key)
    cards = []
    total = 0
    repaired = 0
    for folder in folders:
        lessons = sorted((path for path in folder.iterdir()
                          if path.is_file() and path.suffix.lower() in {".html", ".htm"}
                          and path.name.lower() != "index.html"), key=natural_key)
        total += len(lessons)
        title = label(folder.name)
        count = f'{len(lessons)} lesson' + ("" if len(lessons) == 1 else "s")
        cards.append(f'''<a class="course-card" href="{quote(folder.name)}/">
      <span class="folder-icon" aria-hidden="true"></span>
      <span class="eyebrow">COURSE FOLDER</span>
      <h2>{html.escape(title)}</h2>
      <span class="card-bottom"><span>{count}</span><span>Open folder <span aria-hidden="true">↗</span></span></span>
    </a>''')
        rows = []
        for index, lesson in enumerate(lessons, 1):
            repaired += prepare_lesson(lesson)
            lesson_title = label(re.sub(r"^(?:Lesson[\s-]+)?\d+[\s:.-]*", "", lesson.stem,
                                        flags=re.IGNORECASE))
            rows.append(f'''<li><a class="lesson-link" href="{quote(lesson.name)}">
        <span class="lesson-number">{index:02d}</span><span>{html.escape(lesson_title)}</span>
        <span class="lesson-open" aria-hidden="true">↗</span>
      </a></li>''')
        listing = ('<ol class="lesson-list">' + "\n".join(rows) + '</ol>') if rows else (
            '<div class="empty-state"><h2>No lessons yet</h2>'
            '<p>Lessons will appear here when they are added to this course.</p></div>')
        content = (f'<span class="eyebrow">COURSE FOLDER · {count.upper()}</span>'
                   f'<h1>{html.escape(title)}</h1>'
                   '<p class="intro">Choose a lesson to start learning. '
                   'Use your browser’s Back button to return to this list.</p>' + listing)
        (folder / "index.html").write_text(page(title, content, in_course=True), encoding="utf-8")
    content = (f'<span class="eyebrow">YOUR LEARNING SPACE</span><h1>Explore your courses.</h1>'
               f'<p class="intro">{len(folders)} course folders. {total} lessons. '
               'Open a folder and pick up something new.</p>'
               '<div class="course-grid">' + "\n".join(cards) + '</div>')
    (ROOT / "index.html").write_text(page("All courses", content), encoding="utf-8")
    print(f"Built navigation for {len(folders)} folders and {total} lessons.")
    if repaired:
        print(f"Prepared {repaired} lessons for Live Server compatibility.")


if __name__ == "__main__":
    build()
