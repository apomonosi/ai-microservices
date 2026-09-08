from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

from . import clipboard
from .clipboard import ClipboardError
from .core import (
    ConfigError,
    EngineError,
    Service,
    list_services,
    load_models,
    load_service,
    run_service,
    validate_services,
)


def _read_input(args: argparse.Namespace) -> str | None:
    if args.text is not None:
        return args.text
    if args.file is not None:
        try:
            return args.file.read_text()
        except OSError as exc:
            print(f"error: could not read --file '{args.file}': {exc}", file=sys.stderr)
            return None
    if args.stdin:
        return sys.stdin.read()
    try:
        return clipboard.read_text()
    except ClipboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None


def _write_output_file(args: argparse.Namespace, result: str) -> int:
    try:
        args.output.write_text(result)
    except OSError as exc:
        print(f"error: could not write --output '{args.output}': {exc}", file=sys.stderr)
        return 1
    return 0


def _run_headless(args: argparse.Namespace, service: Service, result: str) -> int:
    ok = True

    if args.output is not None:
        ok = _write_output_file(args, result) == 0 and ok

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
                ok = False

    return 0 if ok else 1


def _run_with_review(args: argparse.Namespace, service: Service, input_text: str, result: str) -> int:
    try:
        from PySide6.QtWidgets import QApplication, QDialog

        from .gui.result_inspector import ResultInspector
    except ImportError:
        print(
            "error: the review UI requires PySide6 (pip install -r requirements.txt); "
            "pass --no-gui to skip it",
            file=sys.stderr,
        )
        return 1

    app = QApplication.instance() or QApplication(sys.argv[:1])
    dialog = ResultInspector(service, input_text, result)
    outcome = dialog.exec()

    ok = True
    if outcome == QDialog.DialogCode.Accepted:
        if service.clipboard_on_accept == "replace":
            try:
                clipboard.write_text(result)
            except ClipboardError as exc:
                print(f"error: {exc}", file=sys.stderr)
                ok = False
        if args.output is not None:
            ok = _write_output_file(args, result) == 0 and ok
    return 0 if ok else 1


def _execute_service(args: argparse.Namespace, service: Service) -> int:
    """Read input, run the service, and route the result through the
    review dialog or the headless path. Shared by `run` (service given by
    id) and `picker` (service chosen interactively).
    """
    input_text = _read_input(args)
    if input_text is None:
        return 1
    if not input_text.strip():
        print("error: no input text (clipboard/--text/--file/--stdin was empty)", file=sys.stderr)
        return 1

    try:
        result = run_service(service, input_text)
    except (ConfigError, EngineError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result)

    if args.no_gui:
        return _run_headless(args, service, result)
    return _run_with_review(args, service, input_text, result)


def cmd_run(args: argparse.Namespace) -> int:
    try:
        service = load_service(args.service_id)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return _execute_service(args, service)


def cmd_picker(args: argparse.Namespace) -> int:
    services = list_services()
    if not services:
        print("error: no services defined in services/", file=sys.stderr)
        return 1

    try:
        from PySide6.QtWidgets import QApplication, QDialog

        from .gui.picker import ActionPicker
    except ImportError:
        print("error: the picker requires PySide6 (pip install -r requirements.txt)", file=sys.stderr)
        return 1

    app = QApplication.instance() or QApplication(sys.argv[:1])
    dialog = ActionPicker(services)
    if dialog.exec() != QDialog.DialogCode.Accepted or dialog.selected_service is None:
        return 0  # user cancelled; not an error

    return _execute_service(args, dialog.selected_service)


def _filter_services(services: list[Service], category: str | None, query: str | None) -> list[Service]:
    if category:
        services = [s for s in services if s.category == category]
    if query:
        q = query.lower()
        services = [s for s in services if q in f"{s.id} {s.name} {s.category} {s.description}".lower()]
    return services


def _print_service_rows(services: list[Service]) -> None:
    for s in sorted(services, key=lambda s: (s.category, s.id)):
        print(f"{s.id:28s} {s.category:16s} {s.name}")


def cmd_service_list(args: argparse.Namespace) -> int:
    services = _filter_services(list_services(), args.category, args.query)
    if not services:
        print("no matching services", file=sys.stderr)
        return 0
    _print_service_rows(services)
    return 0


def cmd_service_show(args: argparse.Namespace) -> int:
    try:
        service = load_service(args.service_id)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        models = load_models()
    except ConfigError:
        models = {}
    profile = models.get(service.model)
    model_line = (
        f"{service.model}  ->  {profile.model} @ {profile.url}"
        if profile is not None
        else f"{service.model}  (not found in models.yaml)"
    )

    print(f"id:                  {service.id}")
    print(f"name:                {service.name}")
    print(f"category:            {service.category}")
    print(f"model:               {model_line}")
    print(f"review:              {service.review}")
    print(f"clipboard_on_accept: {service.clipboard_on_accept}")
    if service.description:
        print(f"description:         {service.description}")
    print()
    print("prompt.system:")
    print(textwrap.indent(service.system_prompt.rstrip(), "    "))
    return 0


def cmd_service_search(args: argparse.Namespace) -> int:
    services = list_services()
    q = args.query.lower()
    matches = [
        s for s in services if q in f"{s.id} {s.name} {s.category} {s.description} {s.system_prompt}".lower()
    ]
    if not matches:
        print(f"no services match '{args.query}'", file=sys.stderr)
        return 0
    _print_service_rows(matches)
    return 0


def cmd_service_categories(args: argparse.Namespace) -> int:
    counts: dict[str, int] = {}
    for s in list_services():
        counts[s.category] = counts.get(s.category, 0) + 1
    for category in sorted(counts):
        print(f"{category:20s} {counts[category]:3d}")
    return 0


def cmd_service_validate(args: argparse.Namespace) -> int:
    problems = validate_services(only_id=args.service_id)
    if not problems:
        print(f"{args.service_id}: OK" if args.service_id else "All services OK")
        return 0
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1


def _add_execution_args(parser: argparse.ArgumentParser) -> None:
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--text", help="Use this text instead of reading the clipboard")
    input_group.add_argument("--file", type=Path, metavar="PATH", help="Read input from this file")
    input_group.add_argument(
        "--stdin", action="store_true", help="Read input from stdin (for piping: `cat x | ai-actions run ...`)"
    )
    parser.add_argument(
        "--output", type=Path, metavar="PATH", help="Also write the result to this file (for piping onward)"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Skip the review dialog; just print/write the result (optionally with --replace-clipboard)",
    )
    parser.add_argument(
        "--replace-clipboard",
        action="store_true",
        help="With --no-gui: write the result to the clipboard unreviewed. Ignored otherwise "
        "(the review dialog's Accept & Copy controls this instead).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-actions")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a service against clipboard, --file, --stdin or --text input")
    run_p.add_argument("service_id")
    _add_execution_args(run_p)
    run_p.set_defaults(func=cmd_run)

    picker_p = sub.add_parser("picker", help="Choose a service from a searchable list, then run it")
    _add_execution_args(picker_p)
    picker_p.set_defaults(func=cmd_picker)

    list_p = sub.add_parser("list", help="List available services (alias for `service list`)")
    list_p.add_argument("--category", help="Only show this category")
    list_p.add_argument("--query", help="Only show services matching this text")
    list_p.set_defaults(func=cmd_service_list)

    service_p = sub.add_parser("service", help="Inspect and manage the service library")
    service_sub = service_p.add_subparsers(dest="service_command", required=True)

    svc_list_p = service_sub.add_parser("list", help="List services")
    svc_list_p.add_argument("--category", help="Only show this category")
    svc_list_p.add_argument("--query", help="Only show services matching this text")
    svc_list_p.set_defaults(func=cmd_service_list)

    svc_show_p = service_sub.add_parser("show", help="Show full details (including the prompt) of one service")
    svc_show_p.add_argument("service_id")
    svc_show_p.set_defaults(func=cmd_service_show)

    svc_search_p = service_sub.add_parser(
        "search", help="Search id/name/category/description/prompt text across all services"
    )
    svc_search_p.add_argument("query")
    svc_search_p.set_defaults(func=cmd_service_search)

    svc_categories_p = service_sub.add_parser("categories", help="List categories in use, with counts")
    svc_categories_p.set_defaults(func=cmd_service_categories)

    svc_validate_p = service_sub.add_parser(
        "validate", help="Check service manifests (and their model references) for problems"
    )
    svc_validate_p.add_argument("service_id", nargs="?", help="Validate only this service (default: all)")
    svc_validate_p.set_defaults(func=cmd_service_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
