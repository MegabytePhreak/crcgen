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

import argparse
import sys
from typing import Iterator, List, Sequence, Tuple


def lfsr_shift_bit(
    poly: Sequence[int], cur_state: Sequence[int], data: int
) -> List[int]:

    next_state = list(cur_state)
    state_msb = next_state[-1]

    for j in range(len(cur_state) - 1, 0, -1):
        if poly[j] != 0:
            next_state[j] = next_state[j - 1] ^ state_msb ^ data
        else:
            next_state[j] = next_state[j - 1]
    next_state[0] = state_msb ^ data

    return next_state


def lfsr_shift_serial(
    poly: Sequence[int], cur_state: Sequence[int], data: Sequence[int]
) -> Sequence[int]:

    next_state = list(cur_state)

    for dbit in data:
        next_state = lfsr_shift_bit(poly, next_state, dbit)

    return next_state


def int_to_poly(length: int, poly: int) -> Sequence[int]:
    ret = [0] * length
    for i in range(length):
        if (poly & 1) != 0:
            ret[i] = 1
        poly = poly >> 1
    return ret


def poly_to_int(poly: Sequence[int]) -> int:
    ret = 0
    for i, bit in enumerate(poly):
        if bit != 0:
            ret |= 1 << i
    return ret


def poly_to_str(poly: Sequence[int]) -> str:
    ret = "x^{}".format(len(poly))
    for i, bit in enumerate(reversed(poly)):
        i = len(poly) - i - 1
        if bit != 0:
            ret += " + x^{}".format(i) if i > 1 else " + x" if i == 1 else " + 1"
    return ret


def build_crc_matrices(
    poly: Sequence[int], dwidth: int, reflect_input: bool = False
) -> Tuple[Sequence[Sequence[int]], Sequence[Sequence[int]]]:

    propagate_state_bits = []
    for i in range(len(poly)):
        nulldata = [0] * dwidth
        state = [0] * len(poly)
        state[i] = 1
        propagate_state_bits.append(lfsr_shift_serial(poly, state, nulldata))

    propagate_data_bits = []
    data_range = range(dwidth)
    # We will naturally reflect the input relative to the normal convention
    # for CRCs by going 0-up, reverse the data if not desired
    if not reflect_input:
        data_range = reversed(data_range)
    for i in data_range:
        data = [0] * dwidth
        data[i] = 1
        nullstate = [0] * len(poly)
        propagate_data_bits.append(lfsr_shift_serial(poly, nullstate, data))

    return (propagate_state_bits, propagate_data_bits)


def gen_vhdl_package(
    cmdline: str,
    name: str,
    poly: Sequence[int],
    dwidth: int,
    state_matrix: Sequence[Sequence[int]],
    data_matrix: Sequence[Sequence[int]],
):

    lines = []

    lines.append("----------------------------------------")
    lines.append("-- Parallel CRC Calculation Package")
    lines.append("-- CRC width:{} data width: {}".format(len(poly), dwidth))
    lines.append(
        "-- polynomial: {} (0x{:X})".format(poly_to_str(poly), poly_to_int(poly))
    )
    lines.append("-- Generated with crcgen")
    lines.append("-- https://github.com/MegabytePhreak/crcgen")
    lines.append("-- arguments: {}".format(cmdline))
    lines.append("-- SPDX-License-Identifier: 0BSD")
    lines.append("----------------------------------------")
    lines.append("")
    lines.append("library ieee;")
    lines.append("use ieee.std_logic_1164.all;")
    lines.append("")
    lines.append("package {}_pkg is ".format(name))
    lines.append("")
    lines.append(
        "    function {}(state: std_logic_vector({} downto 0); data: std_logic_vector({} downto 0)) return std_logic_vector;".format(
            name, len(poly) - 1, dwidth - 1
        )
    )
    lines.append("")
    lines.append("end {}_pkg;".format(name))
    lines.append("")
    lines.append("library ieee;")
    lines.append("use ieee.std_logic_1164.all;")
    lines.append("")
    lines.append("package body {}_pkg is".format(name))
    lines.append("")
    lines.append(
        "    function {}(state: std_logic_vector({} downto 0); data: std_logic_vector({} downto 0)) return std_logic_vector is".format(
            name, len(poly) - 1, dwidth - 1
        )
    )
    lines.append(
        "        variable next_state : std_logic_vector({} downto 0);".format(
            len(poly) - 1
        )
    )
    lines.append("    begin")
    for i in range(len(poly)):
        next_state = ""
        first = True
        for state_index, propagation in enumerate(state_matrix):
            if propagation[i] != 0:
                if first:
                    next_state = "state({})".format(state_index)
                    first = False
                else:
                    next_state += " xor state({})".format(state_index)
        for data_index, propagation in enumerate(data_matrix):
            if propagation[i] != 0:
                next_state += " xor data({})".format(data_index)
        lines.append("        next_state({}) := {};".format(i, next_state))
    lines.append("        return next_state;")
    lines.append("    end {};".format(name))
    lines.append("")
    lines.append("end {}_pkg;".format(name))
    lines.append("")

    return "\n".join(lines)


PRESETS = {"CRC5-USB": (5, 0x5), "CRC32": (32, 0x04C11DB7)}
