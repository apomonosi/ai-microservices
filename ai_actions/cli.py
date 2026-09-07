from __future__ import annotations

import argparse
import sys

from . import clipboard
from .clipboard import ClipboardError
from .core import ConfigError, EngineError, list_services, load_service, run_service


def cmd_run(args: argparse.Namespace) -> int:
    try:
        service = load_service(args.service_id)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.text is not None:
        input_text = args.text
    else:
        try:
            input_text = clipboard.read_text()
        except ClipboardError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    if not input_text.strip():
        print("error: no input text (clipboard/--text was empty)", file=sys.stderr)
        return 1

    try:
        result = run_service(service, input_text)
    except (ConfigError, EngineError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result)

    if args.replace_clipboard:
        if service.clipboard_on_accept != "replace":
            print(
                f"note: service '{service.id}' does not declare clipboard_on_accept: replace; not writing clipboard",
                file=sys.stderr,
            )
        else:
            try:
                clipboard.write_text(result)
            except ClipboardError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for service in list_services():
        print(f"{service.id:20s} {service.category:12s} {service.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-actions")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a service against clipboard or --text input")
    run_p.add_argument("service_id")
    run_p.add_argument("--text", help="Use this text instead of reading the clipboard")
    run_p.add_argument(
        "--replace-clipboard",
        action="store_true",
        help=(
            "Write the result back to the clipboard if the service allows it. "
            "No review step exists yet (Phase 2 adds one) — only pass this once "
            "you're ready to trust the result unreviewed."
        ),
    )
    run_p.set_defaults(func=cmd_run)

    list_p = sub.add_parser("list", help="List available services")
    list_p.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
