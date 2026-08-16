from app.chunking import chunk_text


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