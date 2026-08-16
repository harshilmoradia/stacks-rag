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