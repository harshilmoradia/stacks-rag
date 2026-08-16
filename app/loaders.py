import io

from pypdf import PdfReader


def load_text_bytes(raw: bytes) -> str:
    return raw.decode("utf-8", errors="ignore")


def load_pdf_bytes(raw: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_document(filename: str, raw: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return load_pdf_bytes(raw)
    if lower.endswith((".txt", ".md", ".markdown")):
        return load_text_bytes(raw)
    raise ValueError(f"Unsupported file type: {filename}")