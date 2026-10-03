from pathlib import Path

from pypdf import PdfReader
from docx import Document
from logger_config import logger

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


def parse_document(filename):
    """
    Extract text from a supported document.

    Returns:
        dict: filename, file type, and extracted text.
    """

    path = Path(filename).expanduser().resolve()

    if not path.is_file():
        logger.error(f"Document not found: {path}")
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported file type: {extension}")
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == ".pdf":
        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):
            text = page.extract_text() or ""

            pages.append(
                f"[Page {page_number}]\n{text}"
            )

        content = "\n\n".join(pages)

    elif extension == ".docx":
        document = Document(str(path))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        content = "\n".join(paragraphs)

    else:
        content = path.read_text(
            encoding="utf-8-sig"
        )

    if not content.strip():
        logger.error(
            "No readable text found in document. "
            "The PDF may require OCR."
        )
        raise ValueError(
            "No readable text found in document. "
            "The PDF may require OCR."
        )

    return {
        "filename": path.name,
        "file_type": extension,
        "text": content,
    }