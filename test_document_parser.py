from documents.parser import parse_document


def main():
    filename = input(
        "Enter document path: "
    ).strip()

    result = parse_document(filename)

    print("\nFilename:", result["filename"])
    print("File type:", result["file_type"])
    print("Extracted characters:", len(result["text"]))

    print("\n--- Extracted Text Preview ---\n")
    print(result["text"][:3000])


if __name__ == "__main__":
    main()
