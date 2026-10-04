from pathlib import Path

from documents.document_store import (
    initialize_store,
    save_summary,
    find_document,
    list_documents,
    find_by_hash,
    calculate_file_hash,
)


def main():
    initialize_store()

    filename = input(
        "Enter the path of an already parsed document: "
    ).strip()

    if not filename:
        print("[ERROR] No file path provided.")
        return

    path = Path(filename).expanduser()

    if not path.is_file():
        print(f"[ERROR] File not found: {path}")
        return

    # Use a sample summary to test storage independently
    # of Ollama and document parsing.
    summary = input(
        "Enter a short test summary: "
    ).strip()

    if not summary:
        print("[ERROR] Summary cannot be empty.")
        return

    try:
        record = save_summary(
            filename=str(path),
            summary=summary,
        )

        print("\n[SAVED]")
        print("Document ID:", record["document_id"])
        print("Filename:", record["filename"])

        print("\n[SEARCH]")
        matches = find_document(path.name)

        for document in matches:
            print(
                document["filename"],
                "->",
                document["summary"]
            )

        print("\n[HASH MATCHES]")
        print(
            len(find_by_hash(
                calculate_file_hash(path)
            )),
            "matching record(s)"
        )

        print("\n[LIBRARY]")
        for document in list_documents():
            print(document)

    except Exception as exc:
        print(f"[ERROR] {exc}")


if __name__ == "__main__":
    main()
