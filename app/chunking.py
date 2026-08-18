import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    source: str


def chunk_text(text: str, source: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    step = chunk_size - chunk_overlap

    while start < len(words):
        window = words[start : start + chunk_size]
        chunk_str = " ".join(window).strip()
        if chunk_str:
            chunks.append(Chunk(text=chunk_str, chunk_index=index, source=source))
            index += 1
        start += step

    return chunks


def chunk_by_headings(text: str, source: str, max_words: int) -> list[Chunk]:
    sections = re.split(r"(?=^#{1,6} .+$)", text, flags=re.MULTILINE)

    chunks: list[Chunk] = []
    index = 0
    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section.split()) <= max_words:
            chunks.append(Chunk(text=section, chunk_index=index, source=source))
            index += 1
        else:
            overlap = min(100, max_words // 4)
            for sub in chunk_text(section, source=source, chunk_size=max_words, chunk_overlap=overlap):
                chunks.append(Chunk(text=sub.text, chunk_index=index, source=source))
                index += 1

    return chunks


def chunk_document(text: str, filename: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    if filename.lower().endswith((".md", ".markdown")):
        return chunk_by_headings(text, source=filename, max_words=chunk_size)
    return chunk_text(text, source=filename, chunk_size=chunk_size, chunk_overlap=chunk_overlap)