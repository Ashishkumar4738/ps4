from documents.parser import parse_document
from documents.summarizer import summarize_document


def main():
    filename = input(
        "Enter document path: "
    ).strip()

    if not filename:
        print("[ERROR] No file path entered.")
        return

    try:
        document = parse_document(filename)

        print("\n[DOCUMENT] Text extraction complete")
        print(
            f"[DOCUMENT] Characters: "
            f"{len(document['text'])}"
        )

        result = summarize_document(document)

        print("\n" + "=" * 60)
        print("NOVA DOCUMENT SUMMARY")
        print("=" * 60)

        print("\nFile:", result["filename"])
        print("Chunks:", result["chunk_count"])

        print("\n" + result["summary"])

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
