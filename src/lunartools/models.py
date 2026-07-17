from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _clean(data: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in data.items():
        if value is None or value == "":
            continue
        out[key] = value
    return out


@dataclass
class SolveResult:
    token: str
    solve_ms: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "SolveResult":
        return cls(token=data.get("token", ""), solve_ms=int(data.get("solve_ms", 0)))


@dataclass
class OtpResult:
    id: str
    otp_code: str
    imap_email: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "OtpResult":
        return cls(
            id=data.get("id", ""),
            otp_code=data.get("otp_code", ""),
            imap_email=data.get("imap_email") or None,
        )


@dataclass
class CountResult:
    id: str
    count: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "CountResult":
        return cls(id=data.get("id", ""), count=int(data.get("count", 0)))


@dataclass
class WebhookResult:
    status: str
    count: int
    delivered: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "WebhookResult":
        return cls(
            status=data.get("status", ""),
            count=int(data.get("count", 0)),
            delivered=int(data.get("delivered", 0)),
        )


@dataclass
class EmbedField:
    name: str
    value: str
    inline: bool = False

    def to_json(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"name": self.name, "value": self.value}
        if self.inline:
            data["inline"] = True
        return data


@dataclass
class EmbedFooter:
    text: str
    icon_url: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        return _clean({"text": self.text, "icon_url": self.icon_url})


@dataclass
class EmbedAuthor:
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        return _clean({"name": self.name, "url": self.url, "icon_url": self.icon_url})


@dataclass
class EmbedMedia:
    url: str

    def to_json(self) -> Dict[str, Any]:
        return {"url": self.url}


@dataclass
class Embed:
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    timestamp: Optional[str] = None
    footer: Optional[EmbedFooter] = None
    image: Optional[EmbedMedia] = None
    thumbnail: Optional[EmbedMedia] = None
    author: Optional[EmbedAuthor] = None
    fields: List[EmbedField] = field(default_factory=list)

    def to_json(self) -> Dict[str, Any]:
        data = _clean(
            {
                "title": self.title,
                "description": self.description,
                "url": self.url,
                "color": self.color,
                "timestamp": self.timestamp,
                "footer": self.footer.to_json() if self.footer else None,
                "image": self.image.to_json() if self.image else None,
                "thumbnail": self.thumbnail.to_json() if self.thumbnail else None,
                "author": self.author.to_json() if self.author else None,
            }
        )
        if self.fields:
            data["fields"] = [f.to_json() for f in self.fields]
        return data


@dataclass
class WebhookPayload:
    content: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    embeds: List[Embed] = field(default_factory=list)

    def to_json(self) -> Dict[str, Any]:
        data = _clean(
            {
                "content": self.content,
                "username": self.username,
                "avatar_url": self.avatar_url,
            }
        )
        if self.embeds:
            data["embeds"] = [e.to_json() for e in self.embeds]
        return data
