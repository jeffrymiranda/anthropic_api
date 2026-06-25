import os
from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pydantic import Field

SUPPORTED_EXTENSIONS = ("pdf", "docx")


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(description="Path to the PDF or DOCX file to convert"),
) -> str:
    """Read a PDF or DOCX file from disk and convert its contents to markdown.

    Reads the file at the given path, infers the document type from its file
    extension, and returns the document's contents as markdown-formatted text.
    Only PDF and DOCX files are supported.

    When to use:
    - When you have a path to a local PDF or DOCX file and need its text content
      as markdown.

    When not to use:
    - When you already have the document's raw bytes in memory; use
      `binary_document_to_markdown` instead.
    - For unsupported formats (anything other than .pdf or .docx).

    Examples:
    >>> document_path_to_markdown("report.pdf")
    '# Report\\n\\nThe report details...'
    >>> document_path_to_markdown("financials.docx")
    '# Financials\\n\\n...'
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")

    file_type = os.path.splitext(file_path)[1].lstrip(".").lower()
    if file_type not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{file_type}'. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    with open(file_path, "rb") as f:
        binary_data = f.read()

    return binary_document_to_markdown(binary_data, file_type)
