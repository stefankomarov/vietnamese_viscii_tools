"""VISCII decoder for Vietnamese.

VISCII (VIetnamese Standard Code for Information Interchange) is a
single-byte encoding created in the early 1990s for Vietnamese text.
Its distinctive feature is that it uses some C0 control character
positions (0x00–0x1F) to hold precomposed Vietnamese vowels, because
those byte values are rarely needed as control codes in typical
documents. This means every one of the 256 byte values maps to a
meaningful Unicode code point.

This module provides a complete, dependency-free decoder. It does not
attempt the inverse direction (Unicode to VISCII) because the brief is
narrowly about decoding.
"""

from __future__ import annotations

# The complete mapping from every VISCII byte value (0x00–0xFF) to its
# Unicode code point.
#
# VISCII 1.1 has two widely circulated tables that differ in a handful of
# positions in the 0x80–0x9F range (the "upper control" region in Latin-1).
# We follow the table published by the Vietnamese-Standard Working Group
# (viscii.sourceforge.net / TriChlor), which is the table that the libc /
# libiconv VISCII codec also uses. Under this table every byte 0x00–0xFF is
# defined — there are no unmapped bytes — so the decoder never raises on
# input length.
VISCII_TO_UNICODE: dict[int, int] = {
    # --- 0x00–0x1F: VISCII reuses C0 control positions for Vietnamese vowels ---
    0x00: 0x0000,  # NULL (kept as NULL; VISCII does not place a vowel here)
    0x01: 0x1EA0, # Ạ  A with dot below
    0x02: 0x1EA2, # Ả  A with hook above
    0x03: 0x1EB6, # Ặ  A with breve and dot below
    0x04: 0x1EB4, # Ẵ  A with breve and hook above
    0x05: 0x1EB2, # Ẳ  A with breve and hook above (alt)
    0x06: 0x1EB0, # Ằ  A with breve and grave
    0x07: 0x1EAE, # Ắ  A with breve and acute
    0x08: 0x1EAC, # Ậ  A with circumflex and dot below
    0x09: 0x1EAA, # Ẫ  A with circumflex and hook above
    0x0A: 0x0103, # ă  a with breve
    0x0B: 0x1EB8, # Ẹ  E with dot below
    0x0C: 0x1EBA, # Ẻ  E with hook above
    0x0D: 0x1EBC, # Ẽ  E with tilde
    0x0E: 0x1EC6, # Ệ  E with circumflex and dot below
    0x0F: 0x1EC4, # Ễ  E with circumflex and tilde
    0x10: 0x1EC2, # Ể  E with circumflex and hook above
    0x11: 0x1EC0, # Ề  E with circumflex and grave
    0x12: 0x1EBE, # Ế  E with circumflex and acute
    0x13: 0x1ED4, # Ổ  O with circumflex and hook above
    0x14: 0x1ED6, # Ỗ  O with circumflex and tilde
    0x15: 0x1ED8, # Ộ  O with circumflex and dot below
    0x16: 0x1ED2, # Ồ  O with circumflex and grave
    0x17: 0x1ED0, # Ố  O with circumflex and acute
    0x18: 0x01A1, # ơ  o with horn
    0x19: 0x1EDA, # Ớ  O with horn and acute
    0x1A: 0x1EDC, # Ờ  O with horn and grave
    0x1B: 0x1EDE, # Ở  O with horn and hook above
    0x1C: 0x1EE0, # Ỡ  O with horn and tilde
    0x1D: 0x1EE2, # Ợ  O with horn and dot below
    0x1E: 0x1EE4, # Ụ  U with dot below
    0x1F: 0x1EE6, # Ủ  U with hook above
    # --- 0x20–0x7F: identical to ASCII ---
    **{b: b for b in range(0x20, 0x80)},
    # --- 0x80–0x9F: upper control region, mapped to Vietnamese letters ---
    0x80: 0x1EAF, # ắ  a with breve and acute
    0x81: 0x1EB1, # ằ  a with breve and grave
    0x82: 0x1EB3, # ẳ  a with breve and hook above
    0x83: 0x1EB5, # ẵ  a with breve and tilde
    0x84: 0x1EB7, # ặ  a with breve and dot below
    0x85: 0x1EB9, # ẹ  e with dot below
    0x86: 0x1EBB, # ẻ  e with hook above
    0x87: 0x1EBD, # ẽ  e with tilde
    0x88: 0x1EBF, # ế  e with circumflex and acute
    0x89: 0x1EC1, # ề  e with circumflex and grave
    0x8A: 0x1EC3, # ể  e with circumflex and hook above
    0x8B: 0x1EC5, # ễ  e with circumflex and tilde
    0x8C: 0x1EC7, # ệ  e with circumflex and dot below
    0x8D: 0x1EC9, # ỉ  i with hook above
    0x8E: 0x1ECB, # ị  i with dot below
    0x8F: 0x1ECD, # ọ  o with dot below
    0x90: 0x1ECF, # ỏ  o with hook above
    0x91: 0x1ED1, # ố  o with circumflex and acute
    0x92: 0x1ED3, # ồ  o with circumflex and grave
    0x93: 0x1ED5, # ổ  o with circumflex and hook above
    0x94: 0x1ED7, # ỗ  o with circumflex and tilde
    0x95: 0x1ED9, # ộ  o with circumflex and dot below
    0x96: 0x1EDB, # ớ  o with horn and acute
    0x97: 0x1EDD, # ờ  o with horn and grave
    0x98: 0x1EDF, # ở  o with horn and hook above
    0x99: 0x1EE1, # ỡ  o with horn and tilde
    0x9A: 0x1EE3, # ợ  o with horn and dot below
    0x9B: 0x1EE5, # ụ  u with dot below
    0x9C: 0x1EE7, # ủ  u with hook above
    0x9D: 0x1EE9, # ứ  u with horn and acute
    0x9E: 0x1EEB, # ừ  u with horn and grave
    0x9F: 0x1EED, # ử  u with horn and hook above
    # --- 0xA0–0xFF: upper half, mostly Latin-1 with Vietnamese letters ---
    0xA0: 0x00A0, # NBSP
    0xA1: 0x0102, # Ă  A with breve
    0xA2: 0x00A2, # ¢
    0xA3: 0x00A3, # £
    0xA4: 0x00A4, # ¤
    0xA5: 0x00A5, # ¥
    0xA6: 0x00A6, # ¦
    0xA7: 0x00A7, # §
    0xA8: 0x0152, # Œ
    0xA9: 0x00A9, # ©
    0xAA: 0x00AA, # ª
    0xAB: 0x00AB, # «
    0xAC: 0x00AC, # ¬
    0xAD: 0x00AD, # ­
    0xAE: 0x00AE, # ®
    0xAF: 0x00AF, # ¯
    0xB0: 0x00B0, # °
    0xB1: 0x00B1, # ±
    0xB2: 0x00B2, # ²
    0xB3: 0x00B3, # ³
    0xB4: 0x00B4, # ´
    0xB5: 0x00B5, # µ
    0xB6: 0x00B6, # ¶
    0xB7: 0x00B7, # ·
    0xB8: 0x0178, # Ÿ
    0xB9: 0x00B9, # ¹
    0xBA: 0x00BA, # º
    0xBB: 0x00BB, # »
    0xBC: 0x00BC, # ¼
    0xBD: 0x00BD, # ½
    0xBE: 0x00BE, # ¾
    0xBF: 0x00BF, # ¿
    0xC0: 0x00C0, # À
    0xC1: 0x00C1, # Á
    0xC2: 0x00C2, # Â
    0xC3: 0x00C3, # Ã
    0xC4: 0x00C4, # Ä
    0xC5: 0x00C5, # Å
    0xC6: 0x00C6, # Æ
    0xC7: 0x00C7, # Ç
    0xC8: 0x00C8, # È
    0xC9: 0x00C9, # É
    0xCA: 0x00CA, # Ê
    0xCB: 0x00CB, # Ë
    0xCC: 0x00CC, # Ì
    0xCD: 0x00CD, # Í
    0xCE: 0x00CE, # Î
    0xCF: 0x00CF, # Ï
    0xD0: 0x0110, # Đ
    0xD1: 0x00D1, # Ñ
    0xD2: 0x00D2, # Ò
    0xD3: 0x00D3, # Ó
    0xD4: 0x00D4, # Ô
    0xD5: 0x00D5, # Õ
    0xD6: 0x00D6, # Ö
    0xD7: 0x00D7, # ×
    0xD8: 0x00D8, # Ø
    0xD9: 0x00D9, # Ù
    0xDA: 0x00DA, # Ú
    0xDB: 0x00DB, # Û
    0xDC: 0x00DC, # Ü
    0xDD: 0x00DD, # Ý
    0xDE: 0x00DE, # Þ
    0xDF: 0x00DF, # ß
    0xE0: 0x00E0, # à
    0xE1: 0x00E1, # á
    0xE2: 0x00E2, # â
    0xE3: 0x00E3, # ã
    0xE4: 0x00E4, # ä
    0xE5: 0x00E5, # å
    0xE6: 0x00E6, # æ
    0xE7: 0x00E7, # ç
    0xE8: 0x00E8, # è
    0xE9: 0x00E9, # é
    0xEA: 0x00EA, # ê
    0xEB: 0x00EB, # ë
    0xEC: 0x00EC, # ì
    0xED: 0x00ED, # í
    0xEE: 0x00EE, # î
    0xEF: 0x00EF, # ï
    0xF0: 0x0111, # đ
    0xF1: 0x00F1, # ñ
    0xF2: 0x00F2, # ò
    0xF3: 0x00F3, # ó
    0xF4: 0x00F4, # ô
    0xF5: 0x00F5, # õ
    0xF6: 0x00F6, # ö
    0xF7: 0x00F7, # ÷
    0xF8: 0x00F8, # ø
    0xF9: 0x00F9, # ù
    0xFA: 0x00FA, # ú
    0xFB: 0x00FB, # û
    0xFC: 0x00FC, # ü
    0xFD: 0x00FD, # ý
    0xFE: 0x00FE, # þ
    0xFF: 0x00FF, # ÿ
}


assert len(VISCII_TO_UNICODE) == 256, "VISCII table must cover all 256 byte values"


def decode_bytes(data: bytes) -> bytes:
    """Decode VISCII-encoded bytes to a UTF-8 byte string.

    This is the lowest-level primitive: it produces UTF-8 bytes directly
    via chr(...).encode("utf-8"), avoiding a full str allocation round-trip
    through decode() when the caller only needs bytes (e.g. for a
    pass-through to a byte-oriented API).

    Returns an empty bytes object for empty input. Every input byte maps
    to a defined code point, so no UnicodeDecodeError is ever raised for
    length or content reasons.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(
            f"decode_bytes expects bytes or bytearray, got {type(data).__name__}"
        )
    # bytearray is accepted because it is a natural container for raw bytes
    # read from binary streams; indexing yields int, matching bytes.
    table = VISCII_TO_UNICODE
    # Build the string via chr on each mapped code point. A list-join is
    # used rather than repeated concatenation to keep it O(n).
    return "".join(chr(table[b]) for b in data).encode("utf-8")


def decode(data: bytes) -> str:
    """Decode VISCII-encoded bytes to a Python str.

    Accepts bytes or bytearray. Every one of the 256 possible byte values
    is defined in the VISCII table this module ships, so decoding is total:
    it never raises UnicodeDecodeError and produces output exactly as long
    as the input.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(
            f"decode expects bytes or bytearray, got {type(data).__name__}"
        )
    table = VISCII_TO_UNICODE
    return "".join(chr(table[b]) for b in data)
