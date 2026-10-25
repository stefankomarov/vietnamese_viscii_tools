import unittest

from vietnamese_viscii_tools.core import (
    VISCII_TO_UNICODE,
    decode,
    decode_bytes,
)


class TestTable(unittest.TestCase):
    def test_table_has_exactly_256_entries(self):
        self.assertEqual(len(VISCII_TO_UNICODE), 256)

    def test_table_keys_are_zero_through_255(self):
        self.assertEqual(sorted(VISCII_TO_UNICODE.keys()), list(range(256)))

    def test_table_values_are_valid_unicode_scalars(self):
        for b, cp in VISCII_TO_UNICODE.items():
            self.assertIsInstance(cp, int)
            self.assertGreaterEqual(cp, 0)
            self.assertLessEqual(cp, 0x10FFFF)
            # Every value must be representable as a single code point.
            chr(cp)

    def test_ascii_region_is_identity(self):
        for b in range(0x20, 0x80):
            self.assertEqual(VISCII_TO_UNICODE[b], b)

    def test_null_is_null(self):
        # VISCII leaves 0x00 as NULL rather than mapping it to a vowel.
        self.assertEqual(VISCII_TO_UNICODE[0x00], 0x0000)

    def test_no_value_is_undefined_sentinel(self):
        # No accidental 0xFFFD replacement characters in the table itself.
        self.assertNotIn(0xFFFD, VISCII_TO_UNICODE.values())


class TestDecode(unittest.TestCase):
    def test_empty_input_returns_empty_str(self):
        self.assertEqual(decode(b""), "")

    def test_pure_ascii_passes_through(self):
        self.assertEqual(decode(b"Hello, world!"), "Hello, world!")

    def test_ascii_full_range_identity(self):
        raw = bytes(range(0x20, 0x80))
        self.assertEqual(decode(raw), raw.decode("ascii"))

    def test_lowercase_d_with_stroke(self):
        # 0xD0 -> U+0110 (Đ), 0xF0 -> U+0111 (đ)
        self.assertEqual(decode(b"\xd0"), "\u0110")
        self.assertEqual(decode(b"\xf0"), "\u0111")

    def test_upper_control_byte_0x80(self):
        self.assertEqual(decode(b"\x80"), "\u1eaf")  # ắ

    def test_lower_control_byte_0x01(self):
        self.assertEqual(decode(b"\x01"), "\u1ea0")  # Ạ

    def test_full_256_byte_roundtrip_length(self):
        raw = bytes(range(256))
        result = decode(raw)
        self.assertEqual(len(result), 256)
        self.assertEqual(
            result,
            "".join(chr(VISCII_TO_UNICODE[b]) for b in range(256)),
        )

    def test_mixed_ascii_and_viscii(self):
        # "Ti\u1ec9ng Vi\u1ec7t" encoded with VISCII bytes.
        # 0x8D -> U+1EC9 (ỉ), 0x8C -> U+1EC7 (ệ)
        raw = b"Ti\x8dng Vi\x8ct"
        self.assertEqual(decode(raw), "Ti\u1ec9ng Vi\u1ec7t")

    def accept_bytearray(self):
        raw = bytearray([0x54, 0x69, 0x8D, 0x6E, 0x67])
        self.assertEqual(decode(raw), "Ti\u1ec9ng")

    def test_decode_bytes_type_error_on_str(self):
        with self.assertRaises(TypeError):
            decode("not bytes")  # type: ignore[arg-type]

    def test_decode_bytes_type_error_on_int(self):
        with self.assertRaises(TypeError):
            decode(123)  # type: ignore[arg-type]


class TestDecodeBytes(unittest.TestCase):
    def test_empty_input_returns_empty_bytes(self):
        self.assertEqual(decode_bytes(b""), b"")

    def test_ascii_passthrough_utf8_identical(self):
        self.assertEqual(decode_bytes(b"ASCII only"), b"ASCII only")

    def test_viscii_byte_produces_utf8(self):
        # 0x80 -> U+1EAF -> UTF-8 0xE1 0xBA 0xAF
        self.assertEqual(decode_bytes(b"\x80"), "\u1eaf".encode("utf-8"))

    def test_full_range_matches_decode_output_utf8(self):
        raw = bytes(range(256))
        expected = decode(raw).encode("utf-8")
        self.assertEqual(decode_bytes(raw), expected)

    def test_bytearray_accepted(self):
        raw = bytearray([0x54, 0x69, 0x8D, 0x6E, 0x67])
        self.assertEqual(decode_bytes(raw), "Ti\u1ec9ng".encode("utf-8"))

    def test_type_error_on_str(self):
        with self.assertRaises(TypeError):
            decode_bytes("not bytes")  # type: ignore[arg-type]

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            decode_bytes(None)  # type: ignore[arg-type]


class TestPackageExports(unittest.TestCase):
    def test_public_names_importable(self):
        import vietnamese_viscii_tools as pkg
        self.assertTrue(hasattr(pkg, "decode"))
        self.assertTrue(hasattr(pkg, "decode_bytes"))
        self.assertTrue(hasattr(pkg, "VISCII_TO_UNICODE"))
        self.assertIs(pkg.decode, decode)
        self.assertIs(pkg.decode_bytes, decode_bytes)
        self.assertIs(pkg.VISCII_TO_UNICODE, VISCII_TO_UNICODE)


if __name__ == "__main__":
    unittest.main()
