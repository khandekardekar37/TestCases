from docx import Document
import json
from pathlib import Path


def extract_docx_sections(file_path: str) -> dict:
    """
    Extract section-wise content from a .docx file.

    Output Structure:
    {
        "document_name": "<file_path>",
        "sections": [
            {
                "feature": "<Heading 1 text>",
                "sub_section": "<Heading 2 text or None>",
                "content": ["para text", ...]
            }
        ]
    }
    """

    doc = Document(file_path)

    data = {
        "document_name": str(file_path),
        "sections": []
    }

    current_feature = None
    current_subsection = None
    buffer = []

    def flush_section():
        nonlocal buffer
        if current_feature and buffer:
            data["sections"].append({
                "feature": current_feature,
                "sub_section": current_subsection,
                "content": buffer
            })
            buffer = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name if para.style else ""

        if style_name == "Heading 1":
            flush_section()
            current_feature = text
            current_subsection = None
            buffer = []
            continue

        if style_name == "Heading 2":
            flush_section()
            current_subsection = text
            buffer = []
            continue

        buffer.append(text)

    flush_section()
    return data


# ---------------- CLI SUPPORT (OPTIONAL) ----------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide SSD .docx path")
        sys.exit(1)

    ssd_path = sys.argv[1]
    output_path = Path(ssd_path).stem + "_structured.json"

    extracted_data = extract_docx_sections(ssd_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    print(f"SSD extracted → {output_path}")
