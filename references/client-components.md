# Inspectable Client Components

Use this guide for client packages with request construction, calculated protocol fields, transport and
response parsing. The examples use fictional addresses and fields; they are not a protocol to copy.
Keep this Skill independent of reference projects, machine paths, credentials and vendor defaults.

## Boundaries that a reader can follow

- `api/`: one endpoint per module, or an endpoint folder when its assembly is substantial. Construct a
  complete request without network I/O: explicit method, full URL, headers, query and body. Keep ordinary
  field dictionaries beside the request. A small body/header function in the same endpoint module is fine.
  Share a substantial common header group only when multiple endpoints really use it; keep endpoint-specific
  fields and the assembly of that group visible. Do not reduce the endpoint to an opaque tuple or dispatcher.
- `algorithms/`: independently callable calculations for business fields such as signatures, encrypted
  tokens and derived device identifiers. These functions accept explicit inputs and return computed values.
  They own field order, encoding rules, key selection and protocol-specific constants. Large private
  implementations may live in `algorithms/internal/`.
- `platforms/`: vendor-neutral capabilities used by the client, such as standalone Request values only when the host has none, standard-library
  encoding/cryptographic wrappers and asynchronous transport. Generic crypto accepts data, keys, IVs and
  algorithm options; it must not select business keys, sessions, versions, URLs or field layouts. Do not
  reimplement a standard primitive when an existing library supplies it. Add wrappers for a shared contract,
  not every single standard-library call. Resource construction remains at the composition boundary.
- `parser/`: offline decode, envelope validation and endpoint result interpretation. Accept full response
  text/bytes or an already decoded mapping, and return clear data or a protocol-specific error. Keep generic
  decoding separate from business status checks where they differ. Shared decode/envelope helpers need not
  become a framework or one directory each.
- Explicit exports: export request builders, business algorithms and parsers through maintained public
  modules and a package-level entry when useful. Use direct re-exports and explicit names. Exporting functions
  does not mean combining their implementations or exporting every internal helper.

The normal call path is `build_request(...) -> await transport.download(request) -> parse_response(...)`.
Callers may use any one of these capabilities independently. A stateful client may retain orchestration,
stream ownership or compatibility mapping, but should use the same public builder and parser functions.

## What parameter encapsulation means

A computed signature is a business parameter API. Moving a static request dictionary into a distant
`params/` module is not, by itself, useful encapsulation. Keep simple fields such as `limit`, `cursor` and
`scene` directly visible in their endpoint. Separate substantial calculations or shared field groups when
that makes their inputs and invariants easier to inspect. For complex bodies, put the body builder beside
the request builder in the endpoint's own module/folder, not behind a chain of relays.

Use the full URL literal in each endpoint. Do not introduce `base_url + path`, host registries or a profile
factory merely to avoid repeating a hostname. A request must show its destination before it reaches
transport. A transport must not infer the method from whether a body exists, add business signatures or
silently reinterpret field values. Preserve `None` versus an empty body and the actual encoding on the wire.

Sign the exact values that will be sent. Reuse one request timestamp, identity and serialized body wherever
the protocol requires them; do not regenerate them independently in a helper, sender or retry. For encrypted
responses, retain per-request decryption material alongside the request without confusing it with the body.

## Framework-owned requests and spider orchestration

When a crawler or workflow framework already supplies Request/Response types, construct and return its
native request directly. Do not introduce a second request dataclass, subclass, envelope, or conversion layer
just to follow the standalone example below. Inspect the installed framework's public constructor and use its
actual parameter names and encodings; examples do not define a replacement framework contract.

Keep endpoint assembly in `api/`, computed business fields in `algorithms/`, response interpretation in
`parser/`, and genuinely shared lower-level capabilities in `platforms/`, outside the spider file. In each
endpoint, lay out the full URL, method, params, headers, cookies and body explicitly at the same visible
level. Use the framework's supported fields (`json`, `data`, bytes, or other native encoding) without hiding
all request options in `**kwargs` or an opaque configuration object. Shared groups may be calculated beside
this assembly. A pure builder may accept a callback/errback supplied by the spider; it must not import a
spider or retain one globally.

The spider owns the readable business sequence: choose inputs, yield/submit the exported API request,
receive the framework response, call the exported parser, and select the next API or yield a result. Keep
framework callback wiring, pagination decisions and runtime context in this orchestration. Keep large field
dictionaries, signatures, protocol decoding and transport implementation out of it. Reuse the framework's
scheduler, retries, middleware, pools and resource lifecycle rather than constructing a competing downloader.
Do not force a framework migration on a standalone client that has no such host.

For example, with a fictional framework whose native constructor supports these exact fields:

```python
# api/list_items.py
from example_framework import Request


def build_list_items_request(cursor: str, token: str, callback: object) -> Request:
    """Build the framework's own Request with every endpoint field visible."""
    return Request(
        method="GET",
        url="https://example.invalid/v1/items",
        params={"cursor": cursor, "limit": "20"},
        headers={"Accept": "application/json", "Authorization": "Bearer " + token},
        cookies={},
        body=None,
        callback=callback,
    )
```

```python
# spiders/items.py — the exports refer to api/ and parser/ implementations.
from ..export import build_list_items_request, parse_list_items


def start_requests(token: str):
    """Start the business flow through a separately encapsulated API."""
    yield build_list_items_request("", token, callback=parse_items)


def parse_items(response):
    """Interpret the response and emit business results."""
    result = parse_list_items(response.text)
    yield from result["items"]
```

The fictional framework import illustrates ownership only. Replace it with the project's real public import,
constructor, response access and callback conventions. Verify the built value is a native framework Request
and passes through its normal scheduling/callback path without a custom conversion.

## Standalone example without a framework Request

This example intentionally uses no base URL, client factory or server layers. It shows one endpoint with
ordinary query fields, one calculated header and one parser. Use the project's native request type when one
already exists rather than adding another solely to follow the example.

`platforms/request.py`:

```python
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Request:
    """HTTP values ready for transmission; no download or signing behavior."""

    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict, repr=False)
    params: Dict[str, str] = field(default_factory=dict)
    body: Optional[bytes] = field(default=None, repr=False)
```

`platforms/crypto.py`:

```python
import hashlib
import hmac


def sha256_hex(data: bytes) -> str:
    """Hash bytes without choosing protocol fields or keys."""
    return hashlib.sha256(data).hexdigest()


def hmac_hex(key: bytes, data: bytes, digest_name: str) -> str:
    """Apply a caller-selected standard HMAC algorithm."""
    return hmac.new(key, data, digest_name).hexdigest()
```

`algorithms/signature.py`:

```python
from typing import Dict
from urllib.parse import urlencode
from ..platforms.crypto import hmac_hex, sha256_hex


def get_request_signature(
    method: str, url: str, params: Dict[str, str], body: bytes,
    timestamp: str, key: bytes,
) -> str:
    """Calculate this fictional protocol's signed field layout, without I/O."""
    query = urlencode(sorted(params.items()))
    message = "\n".join((method, url, query, sha256_hex(body), timestamp))
    return hmac_hex(key, message.encode("utf-8"), "sha256")
```

`api/list_items.py`:

```python
import time
from ..algorithms.signature import get_request_signature
from ..platforms.request import Request


def build_list_items_request(cursor: str, token: str, signing_key: bytes) -> Request:
    """Show every request field and its relationship to the signature."""
    method = "GET"
    url = "https://example.invalid/v1/items"
    params = {"cursor": cursor, "limit": "20"}
    timestamp = str(int(time.time()))
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + token,
        "X-Timestamp": timestamp,
        "X-Signature": get_request_signature(
            method, url, params, b"", timestamp, signing_key
        ),
    }
    return Request(method=method, url=url, headers=headers, params=params, body=None)
```

`parser/response.py`:

```python
import json
from typing import Dict, Union


def parse_list_items(response: Union[str, dict]) -> Dict[str, object]:
    """Decode and validate the complete response before returning business data."""
    payload = json.loads(response) if isinstance(response, str) else response
    if not isinstance(payload, dict):
        raise ValueError("Response must be an object")
    if payload.get("code") != 0:
        raise ValueError("Upstream rejected the request")
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Response has no items list")
    items = []
    for item in data["items"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Invalid item identifier")
        items.append({"id": item["id"], "title": item.get("title", "")})
    return {"items": items, "next_cursor": data.get("next_cursor")}
```

`export.py`:

```python
from .api.list_items import build_list_items_request
from .algorithms.signature import get_request_signature
from .parser.response import parse_list_items
from .platforms.request import Request

__all__ = [
    "build_list_items_request", "get_request_signature", "parse_list_items", "Request"
]
```

With a caller-owned transport, the use site remains three visible steps:

```python
request = build_list_items_request(cursor="", token=token, signing_key=key)
response = await transport.download(request)
result = parse_list_items(response)
```

## Parsing and streaming contracts

Parsers do not read an HTTP client, select accounts, retry, write storage or own scheduling. They must not
turn malformed data, denied requests or unavailable capabilities into a successful empty result. Preserve
real empty success separately. Accept only encodings the upstream actually uses; do not add JSONP or other
formats merely because an example parser supports them. Do not fabricate a unique parser for endpoints
whose supported contract is intentionally the same validated JSON envelope.

For streaming, distinguish framing from event interpretation. The stream consumer owns I/O, cancellation
and closure; a decoder can consume a supplied async iterator, while an event parser takes decoded data and
explicit per-stream state. Preserve partial output when a later read fails. Do not create hidden global
parser state, and do not force a streaming endpoint into a buffered example's shape. Keep pure decoding and
business transformations synchronous unless they actually await input.

## Review the result, not only the directories

Reject these outcomes even if their tests pass:

- An endpoint returns only `(method, path, payload)` and requires another layer to discover its host, headers
  or signature inputs.
- A framework-native request is duplicated by a custom request type or conversion layer.
- A spider embeds endpoint dictionaries, cryptographic calculations or protocol parsers.
- Every endpoint delegates its entire request to a distant builder and merely renames its arguments.
- A folder named `params` contains only moved static dictionaries while computed fields remain in transport.
- A generic crypto helper embeds vendor constants or chooses business keys.
- Parsers are hidden inside network/client methods, or a public parser performs an HTTP read.
- A unified export creates another forwarding chain or imports application startup as a side effect.

Before delivery, preview a complete request without network access; verify signed and transmitted values
match; independently parse a valid, empty, denied and malformed response; exercise partial-stream failure
and closure when applicable; and trace one real build/download/parse flow through the public exports. For
shared cryptographic wrappers, use independent known vectors as well as protocol round trips. Update old
imports and remove draft-only relays; retain only compatibility paths required by real callers.
