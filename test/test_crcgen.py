# Copyright (c) 2020-2021 Paul Roukema
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
# SPDX-License-Identifier: 0BSD
#


import os.path
import types
import unittest

from crcgen.crcgen import (
    build_crc_matrices,
    int_to_poly,
    lfsr_shift_serial,
    poly_to_int,
    poly_to_str,
)

CRC5_USB_POLY = [1, 0, 1, 0, 0]
CRC32_POLY = int_to_poly(32, 0x04C11DB7)


def str_to_bits(string):
    bits = []
    for c in string:
        if c == "1":
            bits.append(1)
        else:
            bits.append(0)
    return bits


class TestConversions(unittest.TestCase):
    def test_int2poly(self):
        self.assertEqual(
            int_to_poly(32, 0x04C11DB7), str_to_bits("11101101101110001000001100100000")
        )
        self.assertEqual(int_to_poly(5, 0x5), str_to_bits("10100"))

    def test_poly2int(self):
        self.assertEqual(
            poly_to_int(str_to_bits("11101101101110001000001100100000")), 0x04C11DB7
        )
        self.assertEqual(poly_to_int(str_to_bits("10100")), 0x5)

    def test_poly2str(self):
        self.assertEqual(
            poly_to_str(str_to_bits("11101101101110001000001100100000")),
            "x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1",
        )
        self.assertEqual(poly_to_str(str_to_bits("10100")), "x^5 + x^2 + 1")


class TestLfsrShiftSerial(unittest.TestCase):
    def test_crc5_usb_nulldata_4(self):
        nulldata = [0] * 4
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [1, 0, 0, 0, 0], nulldata)
        self.assertEqual(shifted, [0, 0, 0, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 1, 0, 0, 0], nulldata)
        self.assertEqual(shifted, [1, 0, 1, 0, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 1, 0, 0], nulldata)
        self.assertEqual(shifted, [0, 1, 0, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 0, 1, 0], nulldata)
        self.assertEqual(shifted, [0, 0, 1, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 0, 0, 1], nulldata)
        self.assertEqual(shifted, [1, 0, 1, 1, 0])

    def test_crc5_usb_nullstate_4(self):
        nullstate = [0] * 5
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [1, 0, 0, 0])
        self.assertEqual(shifted, [1, 0, 1, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 1, 0, 0])
        self.assertEqual(shifted, [0, 0, 1, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 1, 0])
        self.assertEqual(shifted, [0, 1, 0, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 1])
        self.assertEqual(shifted, [1, 0, 1, 0, 0])

    def test_crc5_usb_nulldata_8(self):
        nulldata = [0] * 8
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [1, 0, 0, 0, 0], nulldata)
        self.assertEqual(shifted, [1, 0, 1, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 1, 0, 0, 0], nulldata)
        self.assertEqual(shifted, [0, 1, 0, 1, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 1, 0, 0], nulldata)
        self.assertEqual(shifted, [1, 0, 0, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 0, 1, 0], nulldata)
        self.assertEqual(shifted, [1, 1, 1, 0, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, [0, 0, 0, 0, 1], nulldata)
        self.assertEqual(shifted, [0, 1, 1, 1, 0])

    def test_crc5_usb_nullstate_8(self):
        nullstate = [0] * 5
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(shifted, [0, 1, 1, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual(shifted, [1, 1, 1, 0, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(shifted, [1, 0, 0, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 1, 0, 0, 0, 0])
        self.assertEqual(shifted, [0, 1, 0, 1, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(shifted, [1, 0, 1, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 0, 0, 1, 0, 0])
        self.assertEqual(shifted, [0, 0, 1, 0, 1])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 0, 0, 0, 1, 0])
        self.assertEqual(shifted, [0, 1, 0, 1, 0])
        shifted = lfsr_shift_serial(CRC5_USB_POLY, nullstate, [0, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(shifted, [1, 0, 1, 0, 0])

    def test_crc32_64(self):
        data = [0] * 64
        shifted = lfsr_shift_serial(
            CRC32_POLY, str_to_bits("10000000000000000000000000000000"), data
        )
        self.assertEqual(shifted, str_to_bits("10110001111001101011000010010010"))
        shifted = lfsr_shift_serial(
            CRC32_POLY, str_to_bits("00000000000000000000000000000001"), data
        )
        self.assertEqual(shifted, str_to_bits("11001100101010100000000010011110"))

        nullstate = [0] * 32
        data = [0] * 64
        data[0] = 1
        shifted = lfsr_shift_serial(CRC32_POLY, nullstate, data)
        self.assertEqual(shifted, str_to_bits("11001100101010100000000010011110"))

        data = [0] * 64
        data[63] = 1
        shifted = lfsr_shift_serial(CRC32_POLY, nullstate, data)
        self.assertEqual(shifted, str_to_bits("11101101101110001000001100100000"))


class TestBuildCRCMatrices(unittest.TestCase):
    def test_crc5_usb_4(self):
        prop_state, prop_data = build_crc_matrices(CRC5_USB_POLY, 4, True)
        self.assertEqual(
            prop_state,
            [
                [0, 0, 0, 0, 1],
                [1, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 1, 0, 1],
                [1, 0, 1, 1, 0],
            ],
        )
        self.assertEqual(
            prop_data,
            [
                [1, 0, 1, 1, 0],
                [0, 0, 1, 0, 1],
                [0, 1, 0, 1, 0],
                [1, 0, 1, 0, 0],
            ],
        )

    def test_crc5_usb_4_rev(self):
        prop_state, prop_data = build_crc_matrices(CRC5_USB_POLY, 4, False)
        self.assertEqual(
            prop_state,
            [
                [0, 0, 0, 0, 1],
                [1, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 1, 0, 1],
                [1, 0, 1, 1, 0],
            ],
        )
        self.assertEqual(
            prop_data,
            [
                [1, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 1, 0, 1],
                [1, 0, 1, 1, 0],
            ],
        )

    def test_crc5_usb_8(self):
        prop_state, prop_data = build_crc_matrices(CRC5_USB_POLY, 8, True)
        self.assertEqual(
            prop_state,
            [
                [1, 0, 1, 1, 0],
                [0, 1, 0, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
            ],
        )
        self.assertEqual(
            prop_data,
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 0, 0],
                [1, 0, 0, 0, 1],
                [0, 1, 0, 1, 1],
                [1, 0, 1, 1, 0],
                [0, 0, 1, 0, 1],
                [0, 1, 0, 1, 0],
                [1, 0, 1, 0, 0],
            ],
        )

    def test_crc32_16(self):
        prop_state, prop_data = build_crc_matrices(CRC32_POLY, 16, True)
        self.assertEqual(
            prop_state,
            [
                str_to_bits("00000000000000001000000000000000"),
                str_to_bits("00000000000000000100000000000000"),
                str_to_bits("00000000000000000010000000000000"),
                str_to_bits("00000000000000000001000000000000"),
                str_to_bits("00000000000000000000100000000000"),
                str_to_bits("00000000000000000000010000000000"),
                str_to_bits("00000000000000000000001000000000"),
                str_to_bits("00000000000000000000000100000000"),
                str_to_bits("00000000000000000000000010000000"),
                str_to_bits("00000000000000000000000001000000"),
                str_to_bits("00000000000000000000000000100000"),
                str_to_bits("00000000000000000000000000010000"),
                str_to_bits("00000000000000000000000000001000"),
                str_to_bits("00000000000000000000000000000100"),
                str_to_bits("00000000000000000000000000000010"),
                str_to_bits("00000000000000000000000000000001"),
                str_to_bits("11101101101110001000001100100000"),
                str_to_bits("01110110110111000100000110010000"),
                str_to_bits("00111011011011100010000011001000"),
                str_to_bits("00011101101101110001000001100100"),
                str_to_bits("00001110110110111000100000110010"),
                str_to_bits("00000111011011011100010000011001"),
                str_to_bits("11101110000011100110000100101100"),
                str_to_bits("01110111000001110011000010010110"),
                str_to_bits("00111011100000111001100001001011"),
                str_to_bits("11110000011110010100111100000101"),
                str_to_bits("10010101100001000010010010100010"),
                str_to_bits("01001010110000100001001001010001"),
                str_to_bits("11001000110110011000101000001000"),
                str_to_bits("01100100011011001100010100000100"),
                str_to_bits("00110010001101100110001010000010"),
                str_to_bits("00011001000110110011000101000001"),
            ],
        )
        self.assertEqual(
            prop_data,
            [
                str_to_bits("00011001000110110011000101000001"),
                str_to_bits("00110010001101100110001010000010"),
                str_to_bits("01100100011011001100010100000100"),
                str_to_bits("11001000110110011000101000001000"),
                str_to_bits("01001010110000100001001001010001"),
                str_to_bits("10010101100001000010010010100010"),
                str_to_bits("11110000011110010100111100000101"),
                str_to_bits("00111011100000111001100001001011"),
                str_to_bits("01110111000001110011000010010110"),
                str_to_bits("11101110000011100110000100101100"),
                str_to_bits("00000111011011011100010000011001"),
                str_to_bits("00001110110110111000100000110010"),
                str_to_bits("00011101101101110001000001100100"),
                str_to_bits("00111011011011100010000011001000"),
                str_to_bits("01110110110111000100000110010000"),
                str_to_bits("11101101101110001000001100100000"),
            ],
        )


class TestCrcCalculation(unittest.TestCase):
    @staticmethod
    def step_crc(state_matrix, data_matrix, state, data):
        new_state = [0] * len(state)
        for i, row in enumerate(state_matrix):
            for j, propagate in enumerate(row):
                if propagate != 0:
                    new_state[j] = new_state[j] ^ state[i]
        for i, row in enumerate(data_matrix):
            for j, propagate in enumerate(row):
                if propagate != 0:
                    new_state[j] = new_state[j] ^ data[i]
        return new_state

    def check_crc5_usb_1(self, data, expected):
        prop_state, prop_data = build_crc_matrices(CRC5_USB_POLY, 1, False)
        data = str_to_bits(data)
        state = [1] * 5
        for bit in data:
            state = self.step_crc(prop_state, prop_data, state, [bit])
        # USB CRC5 sample results are reversed and inverted
        expected = str_to_bits(expected)
        expected.reverse()
        expected = [1 - x for x in expected]
        self.assertEqual(state, expected)

    def test_crc5_usb_1(self):
        self.check_crc5_usb_1("00001000111", "10100")
        self.check_crc5_usb_1("10101000111", "10111")
        self.check_crc5_usb_1("01011100101", "11100")
        self.check_crc5_usb_1("00001110010", "01110")
        self.check_crc5_usb_1("10000000000", "10111")

    def check_crc5_usb_11(self, data, expected):
        prop_state, prop_data = build_crc_matrices(CRC5_USB_POLY, 11, True)
        data = str_to_bits(data)
        state = [1] * 5
        state = self.step_crc(prop_state, prop_data, state, data)
        # USB CRC5 sample results are reversed and inverted
        expected = str_to_bits(expected)
        expected.reverse()
        expected = [1 - x for x in expected]
        self.assertEqual(state, expected)

    def test_crc5_usb_11(self):
        self.check_crc5_usb_11("00001000111", "10100")
        self.check_crc5_usb_11("10101000111", "10111")
        self.check_crc5_usb_11("01011100101", "11100")
        self.check_crc5_usb_11("00001110010", "01110")
        self.check_crc5_usb_11("10000000000", "10111")

    def check_crc32_8(self, data, expected):
        # https://reveng.sourceforge.io/crc-catalogue/17plus.htm#crc.cat-bits.32
        # width=32 poly=0x04c11db7 init=0xffffffff refin=true refout=true xorout=0xffffffff
        prop_state, prop_data = build_crc_matrices(CRC32_POLY, 8, True)
        state = [1] * 32
        for word in data:
            data_bits = int_to_poly(8, word)
            state = self.step_crc(prop_state, prop_data, state, data_bits)
        # reflectOut=true, xorOut=0xFFFFFFFF
        expected.reverse()
        expected = [1 - x for x in expected]
        self.assertEqual(state, expected)

    def test_crc32_8(self):
        # Test Vectors from AUTOSAR_SWS_CRCLibrary.pdf
        self.check_crc32_8([0x0, 0x0, 0x0, 0x0], int_to_poly(32, 0x2144DF1C))
        self.check_crc32_8([0xF2, 0x01, 0x83], int_to_poly(32, 0x24AB9D77))
        self.check_crc32_8([0x0F, 0xAA, 0x00, 0x55], int_to_poly(32, 0xB6C9B287))
        self.check_crc32_8([0x00, 0xFF, 0x55, 0x11], int_to_poly(32, 0x32A06212))
        self.check_crc32_8(
            [0x33, 0x22, 0x55, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            int_to_poly(32, 0xB0AE863D),
        )
        self.check_crc32_8([0x92, 0x6B, 0x55], int_to_poly(32, 0x9CDEA29B))
        self.check_crc32_8([0xFF, 0xFF, 0xFF, 0xFF], int_to_poly(32, 0xFFFFFFFF))

    def check_crc32_16(self, data, expected):
        # https://reveng.sourceforge.io/crc-catalogue/17plus.htm#crc.cat-bits.32
        # width=32 poly=0x04c11db7 init=0xffffffff refin=true refout=true xorout=0xffffffff
        prop_state, prop_data = build_crc_matrices(CRC32_POLY, 16, True)
        state = [1] * 32
        for word in data:
            data_bits = int_to_poly(16, word)
            state = self.step_crc(prop_state, prop_data, state, data_bits)
        # reflectOut=true, xorOut=0xFFFFFFFF
        expected.reverse()
        expected = [1 - x for x in expected]
        self.assertEqual(state, expected)

    def test_crc32_16(self):
        # Test Vectors from AUTOSAR_SWS_CRCLibrary.pdf
        self.check_crc32_16([0x0, 0x0], int_to_poly(32, 0x2144DF1C))
        self.check_crc32_16([0xAA0F, 0x5500], int_to_poly(32, 0xB6C9B287))
        self.check_crc32_16([0xFF00, 0x1155], int_to_poly(32, 0x32A06212))
        self.check_crc32_16([0xFFFF, 0xFFFF], int_to_poly(32, 0xFFFFFFFF))
