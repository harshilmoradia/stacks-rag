from app.chunking import chunk_by_headings, chunk_document, chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("", source="a.txt", chunk_size=10, chunk_overlap=2) == []


def test_short_text_returns_single_chunk():
    text = "one two three"
    chunks = chunk_text(text, source="a.txt", chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].source == "a.txt"


def test_overlap_repeats_words_between_chunks():
    words = [str(i) for i in range(20)]
    text = " ".join(words)
    chunks = chunk_text(text, source="a.txt", chunk_size=10, chunk_overlap=3)
    assert len(chunks) >= 2
    first_tail = chunks[0].text.split()[-3:]
    second_head = chunks[1].text.split()[:3]
    assert first_tail == second_head


def test_chunk_overlap_must_be_smaller_than_chunk_size():
    try:
        chunk_text("some text", source="a.txt", chunk_size=5, chunk_overlap=5)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_chunk_indices_are_sequential():
    words = [str(i) for i in range(50)]
    text = " ".join(words)
    chunks = chunk_text(text, source="a.txt", chunk_size=10, chunk_overlap=2)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunk_by_headings_splits_on_each_section():
    text = (
        "# Title\n\n"
        "Intro line.\n\n"
        "## Section A\n"
        "Content for section A.\n\n"
        "## Section B\n"
        "Content for section B.\n"
    )
    chunks = chunk_by_headings(text, source="doc.md", max_words=800)
    assert len(chunks) == 3
    assert chunks[0].text.startswith("# Title")
    assert chunks[1].text.startswith("## Section A")
    assert chunks[2].text.startswith("## Section B")


def test_chunk_by_headings_falls_back_to_sliding_window_for_oversized_section():
    long_body = " ".join(["word"] * 50)
    text = f"## Big Section\n{long_body}"
    chunks = chunk_by_headings(text, source="doc.md", max_words=10)
    assert len(chunks) > 1
    assert all(c.source == "doc.md" for c in chunks)


def test_chunk_document_routes_markdown_to_heading_chunker():
    text = "## Only Section\nSome content here."
    md_chunks = chunk_document(text, filename="notes.md", chunk_size=800, chunk_overlap=100)
    txt_chunks = chunk_document(text, filename="notes.txt", chunk_size=800, chunk_overlap=100)
    assert md_chunks[0].text.startswith("## Only Section")
    assert len(txt_chunks) == 1