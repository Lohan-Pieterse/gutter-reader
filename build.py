#!/usr/bin/env python3
"""Builds privacy/index.html from the app repo's PRIVACY.md.

Run: python3 build.py ../final_comic_version/PRIVACY.md
Handles the subset of Markdown the policy uses: #/## headings, - lists, 1. lists,
paragraphs, **bold**, `code`, bare https links. Blockquotes (maintainer notes) are dropped.
"""
import html
import re
import sys

src = open(sys.argv[1] if len(sys.argv) > 1 else "../final_comic_version/PRIVACY.md").read()


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"(https://[^\s<)]+[^\s<).,])", r'<a href="\1">\1</a>', text)
    text = re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+\w)", r'<a href="mailto:\1">\1</a>', text)
    return text


def blocks(md):
    out, para, items, kind = [], [], [], None

    def flush():
        nonlocal para, items, kind
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
        para, items, kind = [], [], None

    for line in md.splitlines():
        s = line.strip()
        if s.startswith(">"):
            continue
        if not s:
            flush()
        elif s.startswith("## "):
            flush()
            out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "):
            flush()
        elif m := re.match(r"(-|\d+\.)\s+(.*)", s):
            if para:
                flush()
            new_kind = "ul" if m.group(1) == "-" else "ol"
            if kind and kind != new_kind:
                flush()
            kind = new_kind
            items.append(m.group(2))
        elif items and line.startswith(" "):
            items[-1] += " " + s
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


body = blocks(src)
template = open("privacy/template.html").read()
open("privacy/index.html", "w").write(template.replace("<!--BODY-->", body))
print("wrote privacy/index.html")
