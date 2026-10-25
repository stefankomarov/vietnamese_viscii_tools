# vietnamese_viscii_tools

Decodes the VISCII character encoding for Vietnamese into Unicode, mapping all 256 byte values (including the upper control characters that VISCII reuses for precomposed vowels) to code points.

```python
from vietnamese_viscii_tools import decode, decode_bytes, VISCII_TO_UNICODE

# bytes -> str
text = decode(b"Ti\x8dng Vi\x8et")   # 'Ti\u1ec9ng Vi\u1ec7t'

# bytes -> UTF-8 bytes (avoids an intermediate str when you only need bytes)
raw = decode_bytes(b"\x80")          # b'\xe1\xba\xaf'

# the full 256-entry byte-to-code-point table
VISCII_TO_UNICODE[0x80]              # 0x1EAF
```

## Why this exists

VISCII is a single-byte Vietnamese encoding from the early 1990s. Its defining quirk is that it places precomposed Vietnamese vowels into C0 control positions (0x01–0x1F) and the upper control region (0x80–0x9F), because those byte slots are unused as actual control codes in typical text. Python's built-in codecs do not ship a VISCII codec, so reading legacy `.txt` or data files encoded in VISCII requires an explicit table.

This library is intentionally narrow: it only decodes. It does not encode Unicode back to VISCII, and it does not implement VNI, TCVN, or other Vietnamese encodings. The trade-off is a tiny, dependency-free module with one job and one source of truth (the `VISCII_TO_UNICODE` table).

## The edge you will hit

There are two incompatible VISCII tables in circulation that disagree on a handful of positions in the 0x80–0x9F range. This library follows the TriChlor / VISCII 1.1 table (the same one `libiconv` implements), in which every byte 0x00–0xFF is defined. If your bytes came from a source that used the variant table, a few characters in the upper-control region will decode to different — but still valid — Vietnamese letters. The ASCII region (0x20–0x7F) and the Latin-1-style letters (0xA0–0xFF) are identical across both tables, so only a small set of precomposed vowels is affected.

`decode` accepts `bytes` or `bytearray` and returns a `str`; `decode_bytes` accepts the same and returns UTF-8 `bytes`. Both reject `str` and other types with `TypeError`.
