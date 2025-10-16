"""
Monkey patch to fix langchain-groq proxies issue with groq 0.4.2

The issue: groq.Groq.__init__ doesn't accept 'proxies' parameter even though
the base class SyncAPIClient does.

Solution: Wrap groq.Groq to strip out proxies parameter if passed.
"""

import groq as _orig_groq
from typing import Any


class GroqPatched(_orig_groq.Groq):
    """Patched Groq client that ignores 'proxies' parameter"""
    
    def __init__(self, **kwargs: Any):
        # Remove proxies if present (not supported in Groq.__init__)
        kwargs.pop('proxies', None)
        super().__init__(**kwargs)


class AsyncGroqPatched(_orig_groq.AsyncGroq):
    """Patched AsyncGroq client that ignores 'proxies' parameter"""
    
    def __init__(self, **kwargs: Any):
        # Remove proxies if present (not supported in AsyncGroq.__init__)
        kwargs.pop('proxies', None)
        super().__init__(**kwargs)


# Monkey patch the groq module
_orig_groq.Groq = GroqPatched
_orig_groq.AsyncGroq = AsyncGroqPatched

print("[OK] Groq client patched to ignore 'proxies' parameter")


