import ollama

from config import MODEL_NAME


CHUNK_SIZE = 12000


def split_text(text, chunk_size=CHUNK_SIZE):
    """
    Split text into chunks without cutting words.
    """

    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1

        if (
            current_length + word_length > chunk_size
            and current_chunk
        ):
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def ask_llm(prompt):
    """
    Send a prompt to the local Ollama model.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Nova, a document analysis assistant. "
                    "Use only information supported by the supplied "
                    "document text. Do not invent facts. "
                    "If information is missing, say so."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response["message"]["content"].strip()


def summarize_document(document):
    """
    Summarize a document returned by parse_document().
    """

    filename = document["filename"]
    text = document["text"]

    chunks = split_text(text)

    if not chunks:
        raise ValueError("The document contains no text.")

    print(
        f"[DOCUMENT] {filename}"
    )
    print(
        f"[DOCUMENT] Processing {len(chunks)} chunk(s)"
    )

    # Summarize each chunk.
    chunk_summaries = []

    for index, chunk in enumerate(chunks, start=1):
        print(
            f"[DOCUMENT] Summarizing chunk "
            f"{index}/{len(chunks)}"
        )

        summary = ask_llm(
            f"""
Summarize this section of the document.

Preserve important names, dates, amounts, requirements,
decisions, and action items when present.

Do not add information that is not in the text.

DOCUMENT: {filename}
SECTION: {index}/{len(chunks)}

TEXT:
{chunk}
"""
        )

        chunk_summaries.append(summary)

    # Combine section summaries into one final summary.
    combined_summary = "\n\n".join(chunk_summaries)

    print("[DOCUMENT] Creating final summary")

    final_summary = ask_llm(
        f"""
Create a useful final summary of the document using
the section summaries below.

Include:
1. Overview
2. Main points
3. Important dates, names, and amounts
4. Decisions or requirements, if present
5. Action items, if present

Do not invent details. If a category is not covered
by the source, state that it was not specified.

DOCUMENT: {filename}

SECTION SUMMARIES:
{combined_summary}
"""
    )

    return {
        "filename": filename,
        "chunk_count": len(chunks),
        "summary": final_summary,
    }
