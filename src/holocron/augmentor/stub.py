from __future__ import annotations

from pathlib import Path


def augment_nfo(nfo_path: Path, api_key: str) -> None:
    """Augment an NFO file with LLM-generated semantic metadata.

    This is a stub for the planned Component D: LLM Augmentation Engine.
    When implemented, this function will:
      1. Read the existing .nfo file at nfo_path.
      2. Send the movie metadata to an LLM API (using api_key).
      3. Receive deep semantic tags: <theme>, <trope>, <vibe>, <summary_spoilers>.
      4. Inject those tags back into the NFO XML for the Materializer to pick up.

    Args:
        nfo_path: Path to the .nfo file to augment.
        api_key: API key for the LLM service (Claude, OpenAI, etc.).

    Raises:
        NotImplementedError: Always — this component is not yet implemented.
    """
    raise NotImplementedError(
        "Component D (LLM Augmentation) is planned for a future phase. "
        "See DESIGN.md section 6 for the full specification."
    )
