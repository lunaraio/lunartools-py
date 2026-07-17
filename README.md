# lunartools-py

Python SDK for the LunarTools remote APIs: captcha solving, inbox OTP retrieval, and Discord webhook forwarding.

Requests are routed to a specific user's running LunarTools toolbox. The toolbox must be open and connected.

```bash
pip install lunartools-py
```

The package installs as `lunartools`:

```python
from lunartools import LunarTools
```

## Quick start

Initialize once with your Client ID (Settings page in the toolbox), then pass the relevant API key per call.

```python
from lunartools import LunarTools

client = LunarTools("lt_c0467cf9074b81e3a916178e597c9d0d")

otp = client.otp("lt_ik_...", email="softies_archaic_8x@icloud.com", site="nike")
print(otp.otp_code, "from", otp.imap_email)
```

## Inbox API

`otp()` waits for a one-time code to arrive and returns it. Only unread mail is searched, newest first, and the matched message is marked read.

```python
otp = client.otp(
    api_key,
    email="alias@icloud.com",        # required - indexes the inbox
    imap_email="mailbox@icloud.com", # optional - omit to search every connected account
    site="nike",                     # optional - use a built-in parser
    regex=None,                      # optional - your own pattern, first capture group wins
    from_=None,                      # optional - filter by sender
    timeout_ms=60_000,               # optional - default 60s, max 120s
)
```

Omit `imap_email` and the toolbox searches every connected account, then reports which one served the code in `otp.imap_email`.

With no `site` and no `regex`, the toolbox auto-detects the code (4, 6, or 8 characters), falling back to AI if the heuristic finds nothing.

Built-in sites: `bestbuy`, `crunchyroll`, `disney`, `eql`, `funko`, `goat`, `nike`, `privacy`, `samsclub`, `target`, `topps`, `walmart`, `zumiez`.

`from_` has a trailing underscore because `from` is a Python keyword. It is sent as `from` on the wire.

### Counting by subject

Pass a `subject` to count matching mail instead of extracting a code. Useful for win trackers. Returns immediately and marks nothing read.

```python
result = client.count(api_key, email="alias@icloud.com", subject="WINNER")
print(result.count)
```

## Solving API

```python
result = client.solve(
    api_key,
    captcha_type="hcaptcha",
    page_url="https://example.com/checkout",
    site_key="e94865c2-4231-4c25-9c6e-2b797b2b56cf",
    proxy_url=None,  # optional - omit to use the harvester's own proxy
)
print(result.token, result.solve_ms)
```

## Webhooks

Posts a Discord-shaped payload to your forwarder token, which fans out to every Discord URL configured for it. Embeds without a `timestamp` get one automatically.

```python
from lunartools import WebhookPayload, Embed, EmbedField

result = client.webhook("your-webhook-token", WebhookPayload(
    username="LunarTools",
    embeds=[Embed(
        title="Checkout Success",
        color=0x5865F2,
        fields=[EmbedField(name="Site", value="Nike", inline=True)],
    )],
))

print(f"{result.delivered} of {result.count} delivered")
```

The webhook token comes from the toolbox and is not the same as an API key.

## Errors

Every failure raises a `LunarToolsError` carrying the API's code.

```python
from lunartools import LunarToolsError

try:
    otp = client.otp(api_key, email="alias@icloud.com")
except LunarToolsError as error:
    if error.retryable:
        ...  # client_offline, client_disconnected, auth_unavailable, too_many_inflight
    print(error.code, error.status_code)
```

| Code | Meaning |
|---|---|
| `invalid_key` | Unknown API key for this client |
| `key_disabled` | The key exists but is disabled |
| `client_offline` | The toolbox is not connected |
| `imap_not_connected` | No matching IMAP account is connected |
| `unsupported_site` | `site` is not a built-in parser |
| `invalid_regex` | `regex` failed to compile |
| `otp_timeout` | No code arrived before the deadline |
| `no_harvester` | No accepting harvester of that captcha type is open |
| `solve_timeout` | The solve did not finish before the deadline |
| `too_many_inflight` | Too many concurrent requests for this client |

## Options

```python
client = LunarTools(
    "lt_...",
    base_url="https://remote.lunaraio.com",
    timeout=150.0,
)
```

Requests are long-polled and can take up to 120s, so keep `timeout` above your per-request `timeout_ms`. The client is also a context manager:

```python
with LunarTools("lt_...") as client:
    ...
```
