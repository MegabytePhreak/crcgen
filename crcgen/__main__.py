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

from .crcgen import PRESETS, build_crc_matrices, gen_vhdl_package, int_to_poly


class PresetAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        preset = PRESETS[values]
        setattr(namespace, "preset", values)
        setattr(namespace, "length", preset[0])
        setattr(namespace, "poly", preset[1])


def main():
    def auto_int(x):
        return int(x, 0)

    parser = argparse.ArgumentParser(
        description="Parallel CRC HDL implementation generator"
    )
    poly_group = parser.add_mutually_exclusive_group()
    poly_group.add_argument(
        "--preset",
        type=str,
        choices=PRESETS,
        action=PresetAction,
        help="Predefined CRC polynomial to use",
    )
    poly_group.add_argument(
        "-p",
        "--poly",
        type=auto_int,
        default=None,
        help="CRC polynominal in normal (non-reversed, non-reciprocal) form",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=None,
        help="Length of the CRC polynomial in bits",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        required=True,
        help="Parallel data width to implement CRC for",
    )
    parser.add_argument(
        "-r",
        "--reflect-input",
        help="Reflect input data before processing (Default True)",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "-R",
        "--no-reflect-input",
        help="Do not reflect input data before processing",
        action="store_false",
        dest="reflect_input",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["vhdl_package"],
        default="vhdl_package",
        help="Type of output file to write",
    )
    parser.add_argument(
        "--name", type=str, default=None, help="Name of generated function/module"
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output filename (default stdout)",
    )

    args = parser.parse_args()
    if args.length is None or args.poly is None:
        parser.error(
            "Need to specify both polynominal (-p) and length (-l) or use preset (--preset)"
        )
    poly = int_to_poly(args.length, args.poly)
    cmdline = " ".join(sys.argv[1:])
    name = args.name
    if name is None:
        if args.preset is not None:
            name = args.preset.lower().replace("-", "_")
        else:
            name = "crc{}".format(len(poly))
        name += "_{}b".format(args.width)

    matrices = build_crc_matrices(poly, args.width, args.reflect_input)
    args.output_file.write(
        gen_vhdl_package(
            cmdline,
            name,
            poly,
            args.width,
            matrices[0],
            matrices[1],
        )
    )


if __name__ == "__main__":
    main()
