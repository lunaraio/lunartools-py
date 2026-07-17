from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests

from .errors import LunarToolsError
from .models import (
    CountResult,
    OtpResult,
    SolveResult,
    WebhookPayload,
    WebhookResult,
    _clean,
)

DEFAULT_BASE_URL = "https://remote.lunaraio.com"
DEFAULT_WEBHOOK_BASE_URL = "https://www.lunartools.co/api/webhooks"
DEFAULT_TIMEOUT = 150.0


def _require(**fields: Optional[str]) -> None:
    for name, value in fields.items():
        if value is None or not str(value).strip():
            raise LunarToolsError("bad_request", f"{name} is required")


class LunarTools:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        webhook_base_url: str = DEFAULT_WEBHOOK_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._webhook_base_url = webhook_base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()

    def solve(
        self,
        api_key: str,
        *,
        captcha_type: str,
        page_url: str,
        site_key: str,
        proxy_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> SolveResult:
        _require(
            api_key=api_key,
            captcha_type=captcha_type,
            page_url=page_url,
            site_key=site_key,
        )

        data = self._post(
            f"{self._base_url}/solve",
            {
                "api_key": api_key,
                "captcha_type": captcha_type,
                "page_url": page_url,
                "site_key": site_key,
                "proxy_url": proxy_url,
                "timeout_ms": timeout_ms,
            },
        )
        return SolveResult.from_json(data)

    def otp(
        self,
        api_key: str,
        *,
        email: str,
        imap_email: Optional[str] = None,
        from_: Optional[str] = None,
        site: Optional[str] = None,
        regex: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> OtpResult:
        _require(api_key=api_key, email=email)

        data = self._post(
            f"{self._base_url}/imap",
            {
                "api_key": api_key,
                "email": email,
                "imap_email": imap_email,
                "from": from_,
                "site": site,
                "regex": regex,
                "timeout_ms": timeout_ms,
            },
        )
        return OtpResult.from_json(data)

    def count(
        self,
        api_key: str,
        *,
        email: str,
        subject: str,
        imap_email: Optional[str] = None,
        from_: Optional[str] = None,
    ) -> CountResult:
        _require(api_key=api_key, email=email, subject=subject)

        data = self._post(
            f"{self._base_url}/imap",
            {
                "api_key": api_key,
                "email": email,
                "subject": subject,
                "imap_email": imap_email,
                "from": from_,
            },
        )
        return CountResult.from_json(data)

    def webhook(self, token: str, payload: WebhookPayload) -> WebhookResult:
        _require(token=token)

        body = payload.to_json()
        if not body.get("content") and not body.get("embeds"):
            raise LunarToolsError("bad_request", "payload needs content or at least one embed")

        data = self._post(f"{self._webhook_base_url}/{quote(token, safe='')}", body, clean=False)
        return WebhookResult.from_json(data)

    def _post(self, url: str, body: Dict[str, Any], *, clean: bool = True) -> Dict[str, Any]:
        payload = _clean(body) if clean else body

        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )
        except requests.Timeout as exc:
            raise LunarToolsError("timeout", str(exc)) from exc
        except requests.RequestException as exc:
            raise LunarToolsError("network", str(exc)) from exc

        raw = response.text
        try:
            parsed = json.loads(raw) if raw else {}
        except ValueError:
            parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}

        if not response.ok:
            message = parsed.get("message") or parsed.get("error") or raw.strip() or "request failed"
            raise LunarToolsError(parsed.get("code", ""), message, response.status_code)

        return parsed

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "LunarTools":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
