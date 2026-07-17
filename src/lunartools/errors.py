from __future__ import annotations

RETRYABLE_CODES = frozenset(
    {
        "client_offline",
        "client_disconnected",
        "auth_unavailable",
        "too_many_inflight",
    }
)


class LunarToolsError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 0) -> None:
        super().__init__(f"{code}: {message}" if code else message)
        self.code = code
        self.message = message
        self.status_code = status_code

    @property
    def retryable(self) -> bool:
        return self.code in RETRYABLE_CODES
