#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-Format Document Ingestion Engine.

Supports:
- Markdown (.md, .markdown, .qmd)
- PDF (.pdf) via PyMuPDF (fitz)
- Microsoft Word (.docx) via native zipfile & XML element tree
- LaTeX (.tex, .latex)
- Python scripts (.py) & Jupyter Notebooks (.ipynb)
- Structured Data (.json, .yaml, .yml, .csv)
- Plain Text (.txt, .rst, .log)
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@dataclass
class TextBlock:
    """Standardized representation of a single document element."""
    block_id: str
    block_type: str  # 'heading', 'paragraph', 'equation', 'table', 'code', 'list_item'
    text: str
    raw_content: str
    page_num: int = 1
    line_start: int = 1
    line_end: int = 1
    parent_heading: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadedDocument:
    """Container for parsed document."""
    file_path: str
    file_type: str
    title: str
    blocks: List[TextBlock]
    raw_full_text: str
    total_words: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "title": self.title,
            "total_blocks": len(self.blocks),
            "total_words": self.total_words,
            "metadata": self.metadata,
            "blocks": [asdict(b) for b in self.blocks],
        }


class DocumentLoader:
    """Parser that ingests diverse file formats into standardized text blocks."""

    @classmethod
    def load(cls, file_path: str | Path) -> LoadedDocument:
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Target document does not exist: {path}")

        suffix = path.suffix.lower()

        if suffix in [".md", ".markdown", ".qmd"]:
            return cls._load_markdown(path)
        elif suffix == ".pdf":
            return cls._load_pdf(path)
        elif suffix == ".docx":
            return cls._load_docx(path)
        elif suffix in [".tex", ".latex"]:
            return cls._load_latex(path)
        elif suffix == ".ipynb":
            return cls._load_jupyter(path)
        elif suffix == ".py":
            return cls._load_code(path, lang="python")
        elif suffix in [".json", ".jsonl"]:
            return cls._load_json(path)
        elif suffix in [".yaml", ".yml"]:
            return cls._load_yaml(path)
        elif suffix in [".html", ".htm"]:
            return cls._load_html(path)
        else:
            return cls._load_plain_text(path)

    @classmethod
    def _load_markdown(cls, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        blocks: List[TextBlock] = []
        current_heading = None
        doc_title = path.stem

        block_counter = 1
        i = 0
        n = len(lines)

        in_code_block = False
        code_buffer: List[str] = []
        code_start_line = 0

        in_math_block = False
        math_buffer: List[str] = []
        math_start_line = 0

        while i < n:
            line = lines[i]
            stripped = line.strip()

            # Handle Fenced Code Blocks
            if stripped.startswith("```"):
                if in_code_block:
                    code_buffer.append(line)
                    raw = "\n".join(code_buffer)
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="code",
                        text=raw,
                        raw_content=raw,
                        line_start=code_start_line,
                        line_end=i + 1,
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
                    in_code_block = False
                    code_buffer = []
                else:
                    in_code_block = True
                    code_start_line = i + 1
                    code_buffer = [line]
                i += 1
                continue

            if in_code_block:
                code_buffer.append(line)
                i += 1
                continue

            # Handle Display Math Blocks ($$...$$)
            if stripped.startswith("$$"):
                if in_math_block or (stripped.endswith("$$") and len(stripped) > 2):
                    if in_math_block:
                        math_buffer.append(line)
                        raw = "\n".join(math_buffer)
                        end_line = i + 1
                    else:
                        raw = line
                        math_start_line = i + 1
                        end_line = i + 1

                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="equation",
                        text=raw.strip("$ \t\r\n"),
                        raw_content=raw,
                        line_start=math_start_line,
                        line_end=end_line,
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
                    in_math_block = False
                    math_buffer = []
                else:
                    in_math_block = True
                    math_start_line = i + 1
                    math_buffer = [line]
                i += 1
                continue

            if in_math_block:
                math_buffer.append(line)
                i += 1
                continue

            # Empty Line
            if not stripped:
                i += 1
                continue

            # Headings
            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                h_text = heading_match.group(2).strip()
                current_heading = h_text
                if level == 1 and doc_title == path.stem:
                    doc_title = h_text
                blocks.append(TextBlock(
                    block_id=f"B{block_counter:04d}",
                    block_type="heading",
                    text=h_text,
                    raw_content=line,
                    line_start=i + 1,
                    line_end=i + 1,
                    parent_heading=current_heading,
                    metadata={"level": level},
                ))
                block_counter += 1
                i += 1
                continue

            # Tables
            if stripped.startswith("|") and stripped.endswith("|"):
                tbl_lines = [line]
                tbl_start = i + 1
                while i + 1 < n and lines[i + 1].strip().startswith("|"):
                    i += 1
                    tbl_lines.append(lines[i])
                raw = "\n".join(tbl_lines)
                blocks.append(TextBlock(
                    block_id=f"B{block_counter:04d}",
                    block_type="table",
                    text=raw,
                    raw_content=raw,
                    line_start=tbl_start,
                    line_end=i + 1,
                    parent_heading=current_heading,
                ))
                block_counter += 1
                i += 1
                continue

            # Standard Paragraph or List Item
            p_lines = [line]
            p_start = i + 1
            while i + 1 < n:
                next_l = lines[i + 1]
                next_s = next_l.strip()
                if not next_s or next_s.startswith(("#", "```", "$$", "|")):
                    break
                i += 1
                p_lines.append(next_l)

            raw = "\n".join(p_lines)
            clean_text = " ".join(l.strip() for l in p_lines)
            b_type = "list_item" if re.match(r"^(\*|-|\+|\d+\.)\s+", stripped) else "paragraph"

            blocks.append(TextBlock(
                block_id=f"B{block_counter:04d}",
                block_type=b_type,
                text=clean_text,
                raw_content=raw,
                line_start=p_start,
                line_end=i + 1,
                parent_heading=current_heading,
            ))
            block_counter += 1
            i += 1

        return LoadedDocument(
            file_path=str(path),
            file_type="markdown",
            title=doc_title,
            blocks=blocks,
            raw_full_text=text,
            total_words=len(text.split()),
        )

    @classmethod
    def _load_pdf(cls, path: Path) -> LoadedDocument:
        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) is required to parse PDF documents.")

        doc = fitz.open(path)
        blocks: List[TextBlock] = []
        block_counter = 1
        full_text_list = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("blocks")
            for b in page_text:
                # b: (x0, y0, x1, y1, text, block_no, block_type)
                text_content = b[4].strip()
                if not text_content:
                    continue
                full_text_list.append(text_content)

                is_heading = len(text_content.splitlines()) == 1 and len(text_content) < 80
                b_type = "heading" if is_heading else "paragraph"

                blocks.append(TextBlock(
                    block_id=f"B{block_counter:04d}",
                    block_type=b_type,
                    text=" ".join(text_content.split()),
                    raw_content=text_content,
                    page_num=page_idx + 1,
                    metadata={"bbox": [b[0], b[1], b[2], b[3]]},
                ))
                block_counter += 1

        full_raw = "\n\n".join(full_text_list)
        return LoadedDocument(
            file_path=str(path),
            file_type="pdf",
            title=doc.metadata.get("title") or path.stem,
            blocks=blocks,
            raw_full_text=full_raw,
            total_words=len(full_raw.split()),
            metadata=doc.metadata or {},
        )

    @classmethod
    def _load_docx(cls, path: Path) -> LoadedDocument:
        """Parse Word documents natively using zipfile and ElementTree."""
        with zipfile.ZipFile(path) as z:
            xml_content = z.read("word/document.xml")

        root = ET.fromstring(xml_content)
        # XML namespace for WordML
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        blocks: List[TextBlock] = []
        block_counter = 1
        full_text_list = []
        current_heading = None

        for p in root.iterfind(".//w:p", ns):
            texts = [node.text for node in p.iterfind(".//w:t", ns) if node.text]
            p_text = "".join(texts).strip()
            if not p_text:
                continue

            # Check style for heading
            style_elem = p.find(".//w:pPr/w:pStyle", ns)
            style_val = style_elem.attrib.get(f"{{{ns['w']}}}val", "") if style_elem is not None else ""

            is_heading = "heading" in style_val.lower() or "title" in style_val.lower()
            if is_heading:
                current_heading = p_text
                b_type = "heading"
            else:
                b_type = "paragraph"

            full_text_list.append(p_text)
            blocks.append(TextBlock(
                block_id=f"B{block_counter:04d}",
                block_type=b_type,
                text=p_text,
                raw_content=p_text,
                parent_heading=current_heading,
                metadata={"style": style_val},
            ))
            block_counter += 1

        full_raw = "\n\n".join(full_text_list)
        return LoadedDocument(
            file_path=str(path),
            file_type="docx",
            title=path.stem,
            blocks=blocks,
            raw_full_text=full_raw,
            total_words=len(full_raw.split()),
        )

    @classmethod
    def _load_latex(cls, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        blocks: List[TextBlock] = []
        block_counter = 1
        current_heading = None

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i].strip()
            if not line or line.startswith("%"):
                i += 1
                continue

            sec_match = re.search(r"\\(section|subsection|subsubsection)\*?\{([^}]+)\}", line)
            if sec_match:
                current_heading = sec_match.group(2)
                blocks.append(TextBlock(
                    block_id=f"B{block_counter:04d}",
                    block_type="heading",
                    text=current_heading,
                    raw_content=line,
                    line_start=i + 1,
                    line_end=i + 1,
                    parent_heading=current_heading,
                ))
                block_counter += 1
                i += 1
                continue

            if "\\begin{equation}" in line or "\\begin{align}" in line:
                eq_lines = [line]
                eq_start = i + 1
                while i + 1 < n and not ("\\end{equation}" in lines[i] or "\\end{align}" in lines[i]):
                    i += 1
                    eq_lines.append(lines[i])
                raw = "\n".join(eq_lines)
                blocks.append(TextBlock(
                    block_id=f"B{block_counter:04d}",
                    block_type="equation",
                    text=raw,
                    raw_content=raw,
                    line_start=eq_start,
                    line_end=i + 1,
                    parent_heading=current_heading,
                ))
                block_counter += 1
                i += 1
                continue

            p_lines = [line]
            p_start = i + 1
            while i + 1 < n and lines[i + 1].strip() and not lines[i + 1].strip().startswith(("%", "\\section", "\\begin")):
                i += 1
                p_lines.append(lines[i].strip())

            raw = "\n".join(p_lines)
            blocks.append(TextBlock(
                block_id=f"B{block_counter:04d}",
                block_type="paragraph",
                text=" ".join(p_lines),
                raw_content=raw,
                line_start=p_start,
                line_end=i + 1,
                parent_heading=current_heading,
            ))
            block_counter += 1
            i += 1

        return LoadedDocument(
            file_path=str(path),
            file_type="latex",
            title=path.stem,
            blocks=blocks,
            raw_full_text=text,
            total_words=len(text.split()),
        )

    @classmethod
    def _load_jupyter(cls, path: Path) -> LoadedDocument:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        blocks: List[TextBlock] = []
        block_counter = 1
        full_text_list = []

        for cell_idx, cell in enumerate(data.get("cells", [])):
            cell_type = cell.get("cell_type", "code")
            source = "".join(cell.get("source", []))
            if not source.strip():
                continue

            full_text_list.append(source)
            blocks.append(TextBlock(
                block_id=f"B{block_counter:04d}",
                block_type="paragraph" if cell_type == "markdown" else "code",
                text=source,
                raw_content=source,
                metadata={"cell_index": cell_idx, "cell_type": cell_type},
            ))
            block_counter += 1

        full_raw = "\n\n".join(full_text_list)
        return LoadedDocument(
            file_path=str(path),
            file_type="jupyter_notebook",
            title=path.stem,
            blocks=blocks,
            raw_full_text=full_raw,
            total_words=len(full_raw.split()),
        )

    @classmethod
    def _load_code(cls, path: Path, lang: str = "python") -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        blocks = [
            TextBlock(
                block_id="B0001",
                block_type="code",
                text=text,
                raw_content=text,
                metadata={"language": lang},
            )
        ]
        return LoadedDocument(
            file_path=str(path),
            file_type=f"code_{lang}",
            title=path.name,
            blocks=blocks,
            raw_full_text=text,
            total_words=len(text.split()),
        )

    @classmethod
    def _load_json(cls, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        blocks = [
            TextBlock(
                block_id="B0001",
                block_type="structured_data",
                text=formatted,
                raw_content=text,
            )
        ]
        return LoadedDocument(
            file_path=str(path),
            file_type="json",
            title=path.stem,
            blocks=blocks,
            raw_full_text=formatted,
            total_words=len(formatted.split()),
        )

    @classmethod
    def _load_yaml(cls, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        blocks = [
            TextBlock(
                block_id="B0001",
                block_type="structured_data",
                text=text,
                raw_content=text,
            )
        ]
        return LoadedDocument(
            file_path=str(path),
            file_type="yaml",
            title=path.stem,
            blocks=blocks,
            raw_full_text=text,
            total_words=len(text.split()),
        )

    @classmethod
    def _load_plain_text(cls, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        blocks = []
        block_counter = 1

        buf = []
        start_line = 1
        for i, line in enumerate(lines, 1):
            if not line.strip():
                if buf:
                    raw = "\n".join(buf)
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="paragraph",
                        text=" ".join(buf),
                        raw_content=raw,
                        line_start=start_line,
                        line_end=i - 1,
                    ))
                    block_counter += 1
                    buf = []
                start_line = i + 1
            else:
                buf.append(line.strip())

        if buf:
            raw = "\n".join(buf)
            blocks.append(TextBlock(
                block_id=f"B{block_counter:04d}",
                block_type="paragraph",
                text=" ".join(buf),
                raw_content=raw,
                line_start=start_line,
                line_end=len(lines),
            ))

        return LoadedDocument(
            file_path=str(path),
            file_type="plain_text",
            title=path.stem,
            blocks=blocks,
            raw_full_text=text,
            total_words=len(text.split()),
        )

    @classmethod
    def _load_html(cls, path: Path) -> LoadedDocument:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        blocks: List[TextBlock] = []
        doc_title = path.stem
        block_counter = 1
        current_heading = None

        if BeautifulSoup is not None:
            soup = BeautifulSoup(raw_text, "html.parser")
            if soup.title and soup.title.string:
                doc_title = soup.title.string.strip()

            # Prefer main / article container, fallback to body / root
            container = soup.find("main") or soup.find("article") or soup.body or soup

            for el in container.descendants:
                name = getattr(el, "name", None)
                if not name or name not in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "table", "li"]:
                    continue

                # Skip descendants already contained within another matched element of interest
                # to avoid duplicated text blocks (e.g. li inside table, or p inside table/pre)
                if any(getattr(parent, "name", None) in ["p", "pre", "table"] for parent in el.parents):
                    continue

                text_content = el.get_text(separator=" ", strip=True)
                if not text_content:
                    continue

                if name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    current_heading = text_content
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="heading",
                        text=text_content,
                        raw_content=str(el),
                        parent_heading=current_heading,
                        metadata={"level": int(name[1])},
                    ))
                    block_counter += 1
                elif name == "pre":
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="code",
                        text=el.get_text(),
                        raw_content=str(el),
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
                elif name == "table":
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="table",
                        text=text_content,
                        raw_content=str(el),
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
                elif name == "li":
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="list_item",
                        text=text_content,
                        raw_content=str(el),
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
                elif name == "p":
                    is_eq = ("$$" in text_content or "\\[" in text_content or "\\(" in text_content or "formula" in el.get("class", []))
                    blocks.append(TextBlock(
                        block_id=f"B{block_counter:04d}",
                        block_type="equation" if is_eq else "paragraph",
                        text=text_content,
                        raw_content=str(el),
                        parent_heading=current_heading,
                    ))
                    block_counter += 1
        else:
            # Fallback for plain html reading
            text = re.sub(r"<[^>]+>", " ", raw_text)
            return cls._load_plain_text(path)

        return LoadedDocument(
            file_path=str(path),
            file_type="html",
            title=doc_title,
            blocks=blocks,
            raw_full_text=raw_text,
            total_words=sum(len(b.text.split()) for b in blocks),
        )



if __name__ == "__main__":
    if len(sys.argv) > 1:
        doc = DocumentLoader.load(sys.argv[1])
        print(f"Loaded {doc.file_type} document: '{doc.title}' with {len(doc.blocks)} blocks, {doc.total_words} words.")
    else:
        print("Usage: python document_loader.py <path_to_document>")
