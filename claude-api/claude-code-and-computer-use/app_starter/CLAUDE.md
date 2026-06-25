# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`app` (package name in `pyproject.toml`) is a Python package that exposes document-processing tools through an **MCP (Model Context Protocol) server** built on `FastMCP`. The server is named `"docs"` and tools are plain Python functions registered onto it.

## Commands

All commands assume the venv is created and active (`uv venv && source .venv/bin/activate`).

```bash
uv pip install -e .          # Install package in editable/dev mode
uv run main.py               # Start the MCP server (FastMCP, stdio)
uv run pytest                # Run the full test suite
uv run pytest tests/test_document.py                                   # Single file
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown     # Single class
uv run pytest "tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf"   # Single test
```

There is no linter configured. Python `>=3.10` is required.

## Conventions

- **Always apply appropriate type annotations to function arguments** (and return types). Every parameter must be typed; for MCP tools, pair the type with a pydantic `Field(description=...)` as shown below.

## Architecture

- **`main.py`** — The MCP entrypoint. Creates `mcp = FastMCP("docs")`, registers tools onto it, and calls `mcp.run()`. Tools are registered with the call form `mcp.tool()(my_function)` — the function is defined in a `tools/` module and registration is kept separate from definition, so `main.py` stays a thin wiring layer.
- **`tools/`** — One module per concern (`math.py`, `document.py`). Each tool is an ordinary, independently-testable function; it has no dependency on MCP. This separation is deliberate: tests import the functions directly (e.g. `from tools.document import binary_document_to_markdown`) without standing up a server.
- **`tests/`** — `pytest`. Fixtures live in `tests/fixtures/` (real `.docx` / `.pdf` files) and are loaded relative to `__file__`. Tests exercise the tool functions directly, not through the MCP transport.

Document conversion is delegated to the `markitdown` library (`markitdown[docx,pdf]`); `binary_document_to_markdown` wraps bytes in a `BytesIO` + `StreamInfo(extension=...)` and returns `result.text_content`.

## Defining MCP Tools (from README)

Tools are defined as plain Python functions and then registered with the MCP server:

```python
mcp.tool()(my_function)
```

Tool **descriptions** (the docstring) should:

- Begin with a one-line summary.
- Provide a detailed explanation of functionality.
- Explain when to use — and when *not* to use — the tool.
- Include usage examples with expected input/output.

Use `Field` from pydantic for **parameter descriptions** (not bare type hints):

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does"),
) -> ReturnType:
    """Comprehensive docstring here"""
    # Implementation
```

`tools/math.py` is the canonical reference implementation of this convention (one-line summary, "When to use" section, `>>>` examples, `Field`-annotated params). Follow it when adding new tools, then register the function in `main.py`.

### Decorator-style registration (alternate form)

A sibling project (`../../model-context-protocol/cli_project/mcp_server.py`) uses the decorator form instead, and also demonstrates resources and prompts:

```python
@mcp.tool(name="read_doc_contents", description="...")   # tool with explicit name/description
@mcp.resource("docs://documents", mime_type="application/json")   # resource (list/fetch data)
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")  # templated resource
@mcp.prompt(name="format", description="...")            # prompt returning [base.Message]
```

Both the `mcp.tool()(fn)` and `@mcp.tool(...)` forms are valid — `main.py` here uses the former to keep definition and registration separate.
