import argparse
import sys
from .compiler import compile_to_html


def main():
    parser = argparse.ArgumentParser(prog="llm2page", description="Compile MiniDoc DSL to HTML")
    parser.add_argument("input", nargs="?", help="Input .minidoc file (omit to read stdin)")
    parser.add_argument("-o", "--output", default="-", help="Output HTML file (default: stdout)")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            dsl = f.read()
    else:
        dsl = sys.stdin.read()

    html = compile_to_html(dsl)

    if args.output == "-":
        sys.stdout.write(html)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)


if __name__ == "__main__":
    main()