"""
sa_utils.py — Shared utilities for the Synthetic Archaeology project.

Every notebook should start with:

    import sys; sys.path.insert(0, "/path/to/project/root")
    from sa_utils import load_env, PROJECT_ROOT, get_openai_client

This module centralises:
  * .env loading
  * project-relative paths
  * a single OpenAI client constructor (so we never hard-code keys)
  * a polite HTTP session (User-Agent + retry) for all scrapers
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_GENERATED = PROJECT_ROOT / "data" / "generated"

for p in (DATA_RAW, DATA_PROCESSED, DATA_GENERATED):
    p.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Environment / secrets
# -----------------------------------------------------------------------------
def load_env(verbose: bool = True) -> None:
    """Load .env from the project root. Never logs the key itself."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        raise FileNotFoundError(
            f"No .env file at {env_path}. "
            "Copy .env.example to .env and fill in your OPENAI_API_KEY."
        )

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        # tiny fallback parser so notebooks still work without python-dotenv
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

    if verbose:
        has_key = bool(os.getenv("OPENAI_API_KEY"))
        print(f".env loaded. OPENAI_API_KEY present: {has_key}")


def get_openai_client():
    """Return an authenticated OpenAI client without ever printing the key."""
    load_env(verbose=False)
    key = os.getenv("OPENAI_API_KEY")
    if not key or "REPLACE_ME" in key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing or still a placeholder. "
            "Edit your .env file."
        )
    from openai import OpenAI
    return OpenAI(api_key=key)


# -----------------------------------------------------------------------------
# Polite HTTP session for scrapers
# -----------------------------------------------------------------------------
USER_AGENT = (
    "synthetic-archaeology-research/0.1 "
    "(Bartlett B-Pro DfPI Digital Skills 25/26; "
    "contact: student via UCL email)"
)

def make_session(timeout: int = 20):
    """Return a requests.Session with our User-Agent and a retry adapter."""
    import requests
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        from urllib3.util import Retry  # older urllib3

    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        respect_retry_after_header=True,
    )
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.request_timeout = timeout  # convention: read elsewhere as s.request_timeout
    return s


def polite_sleep(seconds: float = 1.0) -> None:
    """Rate-limit helper. Always wait at least this long between requests."""
    time.sleep(seconds)


# -----------------------------------------------------------------------------
# Tiny helper: safe filename
# -----------------------------------------------------------------------------
def safe_filename(s: str, max_len: int = 80) -> str:
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    cleaned = "".join(c if c in keep else "_" for c in s).strip()
    return cleaned[:max_len] or "untitled"
