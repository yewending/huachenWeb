from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

PUBLIC_DIRS = [
    "css",
    "fonts",
    "images",
    "js",
    "mis/images",
    "mis/lunbo",
]

STATIC_HTML = [
    "index.html",
    "about.html",
    "services.html",
    "codes.html",
]

PHP_PAGES = {
    "contact.php": "contact.html",
    "case1.php": "case1.html",
    "case2.php": "case2.html",
    "case3.php": "case3.html",
    "case4.php": "case4.html",
}

CONTACT_INFO = {
    "company_desc": (
        "\u6e56\u5dde\u534e\u5bb8\u88c5\u9970\u6709\u9650\u516c\u53f8\uff0c"
        "\u4e00\u76f4\u79c9\u627f\uff1a\u201c\u8d28\u91cf\u7b2c\u4e00\u3001"
        "\u4fe1\u8a89\u81f3\u4e0a\u201d\u7684\u7ecf\u8425\u7406\u5ff5\uff0c"
        "\u4e13\u4e1a\u4ece\u4e8b\u5ba4\u5185\u5916\u88c5\u4fee\u3001\u8bbe\u8ba1\u670d\u52a1\u3002"
    ),
    "person": "\u4f59\u7ecf\u7406",
    "phone": "131-8520-5025",
    "mobile": "131-8520-5025",
    "mail": "309648094@qq.com",
    "fax": "",
    "qq": "309648094",
    "address": "\u6d59\u6c5f\u7701\u6e56\u5dde\u5e02\u5434\u5174\u533a\u7ea2\u661f\u73af\u7403\u54c1\u724c\u4e2d\u5fc3\u5317\u95e8\u4e09\u697c",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def rewrite_links(content: str) -> str:
    for php_name, html_name in PHP_PAGES.items():
        content = content.replace(php_name, html_name)
    return content


def strip_php_blocks(content: str) -> str:
    return re.sub(r"<\?php.*?\?>", "", content, flags=re.DOTALL)


def render_case(content: str, case_number: int) -> str:
    article_path = ROOT / "mis" / "article" / f"article{case_number}.txt"
    article = html.escape(read_text(article_path).strip()).replace("\n", "<br>\n")
    content = re.sub(
        r"<\?php\s*\$file\s*=.*?fclose\(\$file\);\s*\?>",
        article,
        content,
        flags=re.DOTALL,
    )
    return strip_php_blocks(content)


def render_contact(content: str) -> str:
    content = re.sub(r"<\?php.*?\?>\s*", "", content, count=1, flags=re.DOTALL)

    def replace_info(match: re.Match[str]) -> str:
        key = match.group(1)
        return html.escape(CONTACT_INFO.get(key, ""))

    content = re.sub(
        r"<\?php\s*echo\s+\$info\[['\"]([^'\"]+)['\"]\]\s*\?>",
        replace_info,
        content,
    )
    return strip_php_blocks(content)


def copy_public_assets() -> None:
    for relative_dir in PUBLIC_DIRS:
        source = ROOT / relative_dir
        if source.exists():
            shutil.copytree(
                source,
                OUT / relative_dir,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".DS_Store"),
            )

    write_text(OUT / ".nojekyll", "")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copy_public_assets()

    for file_name in STATIC_HTML:
        content = rewrite_links(read_text(ROOT / file_name))
        write_text(OUT / file_name, content)

    for source_name, output_name in PHP_PAGES.items():
        content = read_text(ROOT / source_name)
        if source_name.startswith("case"):
            case_number = int(source_name.removeprefix("case").removesuffix(".php"))
            content = render_case(content, case_number)
        else:
            content = render_contact(content)
        write_text(OUT / output_name, rewrite_links(content))


if __name__ == "__main__":
    build()
