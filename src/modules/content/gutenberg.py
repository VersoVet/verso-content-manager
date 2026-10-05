"""Convert markdown content to WordPress Gutenberg block format.

Produces native WordPress block markup (<!-- wp:xxx -->) so content
is fully editable in the WordPress block editor.
"""

import re
from html import escape


def markdown_to_gutenberg(markdown_text: str) -> str:
    """Convert markdown text to Gutenberg block markup.

    Handles: headings, paragraphs, bold, italic, lists, separators.
    Each element becomes a separate wp: block.

    Args:
        markdown_text: Markdown content.

    Returns:
        WordPress Gutenberg block markup string.
    """
    lines = markdown_text.strip().split("\n")
    blocks: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Heading
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = _inline_format(heading_match.group(2))
            blocks.append(_wp_heading(text, level))
            i += 1
            continue

        # Unordered list
        if re.match(r"^[-*]\s", line):
            items, i = _collect_list_items(lines, i)
            blocks.append(_wp_list(items))
            continue

        # Separator / horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", line):
            blocks.append(_wp_separator())
            i += 1
            continue

        # Regular paragraph (may span multiple lines)
        para_lines, i = _collect_paragraph(lines, i)
        text = _inline_format(" ".join(para_lines))
        if text:
            blocks.append(_wp_paragraph(text))

    return "\n\n".join(blocks)


def section_to_gutenberg(title: str, content: str) -> str:
    """Convert a section (title + markdown content) to Gutenberg blocks.

    Args:
        title: Section heading text.
        content: Section markdown content (headings already shifted).

    Returns:
        Gutenberg block markup for the complete section.
    """
    blocks: list[str] = []

    # Section heading as h2
    blocks.append(_wp_heading(escape(title), 2))

    # Convert content to blocks
    content_blocks = markdown_to_gutenberg(content)
    if content_blocks:
        blocks.append(content_blocks)

    return "\n\n".join(blocks)


def bibliography_to_gutenberg(
    entries: list[dict],
) -> str:
    """Convert bibliography entries to Gutenberg blocks.

    Args:
        entries: List of dicts with 'formatted' key.

    Returns:
        Gutenberg blocks for bibliography section.
    """
    if not entries:
        return ""

    blocks: list[str] = []
    blocks.append(_wp_separator())
    blocks.append(_wp_heading("Bibliographie", 2))

    items = [escape(e.get("formatted", "")) for e in entries]
    blocks.append(_wp_list(items, ordered=True))

    return "\n\n".join(blocks)


# --- Block builders ---


def _wp_heading(text: str, level: int = 2) -> str:
    """Build a wp:heading block.

    Args:
        text: Heading text (may contain inline HTML).
        level: Heading level (2-6).

    Returns:
        Gutenberg heading block.
    """
    attrs = "" if level == 2 else f' {{"level":{level}}}'
    return f'<!-- wp:heading{attrs} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'


def _wp_paragraph(text: str) -> str:
    """Build a wp:paragraph block.

    Args:
        text: Paragraph text (may contain inline HTML).

    Returns:
        Gutenberg paragraph block.
    """
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def _wp_list(items: list[str], ordered: bool = False) -> str:
    """Build a wp:list block.

    Args:
        items: List of item texts (may contain inline HTML).
        ordered: True for ordered list.

    Returns:
        Gutenberg list block.
    """
    tag = "ol" if ordered else "ul"
    attrs = ' {"ordered":true}' if ordered else ""
    li_parts = "\n".join(f"<!-- wp:list-item -->\n<li>{item}</li>\n<!-- /wp:list-item -->" for item in items)
    return f'<!-- wp:list{attrs} -->\n<{tag} class="wp-block-list">{li_parts}</{tag}>\n<!-- /wp:list -->'


def _wp_separator() -> str:
    """Build a wp:separator block.

    Returns:
        Gutenberg separator block.
    """
    return '<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->'


# --- Helpers ---


def _inline_format(text: str) -> str:
    """Convert inline markdown (bold, italic) to HTML.

    Args:
        text: Text with markdown formatting.

    Returns:
        Text with HTML inline formatting.
    """
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
    return text


def _collect_list_items(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect consecutive list items.

    Args:
        lines: All lines.
        start: Starting index.

    Returns:
        Tuple of (items list, next index).
    """
    items: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        match = re.match(r"^[-*]\s+(.+)$", line)
        if match:
            items.append(_inline_format(match.group(1)))
            i += 1
        else:
            break
    return items, i


def _collect_paragraph(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect consecutive non-special lines as a paragraph.

    Args:
        lines: All lines.
        start: Starting index.

    Returns:
        Tuple of (paragraph lines, next index).
    """
    para: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            break
        if re.match(r"^#{1,6}\s", line) or re.match(r"^[-*]\s", line) or re.match(r"^[-*_]{3,}\s*$", line):
            break
        para.append(line)
        i += 1
    return para, i
