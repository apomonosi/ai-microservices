from __future__ import annotations

import argparse
import sys

from . import clipboard
from .clipboard import ClipboardError
from .core import ConfigError, EngineError, Service, list_services, load_service, run_service


def _read_input(args: argparse.Namespace) -> str | None:
    if args.text is not None:
        return args.text
    try:
        return clipboard.read_text()
    except ClipboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None


def _run_headless(args: argparse.Namespace, service: Service, result: str) -> int:
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


def _run_with_review(service: Service, input_text: str, result: str) -> int:
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

    if outcome == QDialog.DialogCode.Accepted and service.clipboard_on_accept == "replace":
        try:
            clipboard.write_text(result)
        except ClipboardError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    return 0


def _execute_service(args: argparse.Namespace, service: Service) -> int:
    """Read input, run the service, and route the result through the
    review dialog or the headless path. Shared by `run` (service given by
    id) and `picker` (service chosen interactively).
    """
    input_text = _read_input(args)
    if input_text is None:
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

    if args.no_gui:
        return _run_headless(args, service, result)
    return _run_with_review(service, input_text, result)


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


def cmd_list(args: argparse.Namespace) -> int:
    for service in list_services():
        print(f"{service.id:20s} {service.category:12s} {service.name}")
    return 0


def _add_execution_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", help="Use this text instead of reading the clipboard")
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Skip the review dialog; just print the result (optionally with --replace-clipboard)",
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

    run_p = sub.add_parser("run", help="Run a service against clipboard or --text input")
    run_p.add_argument("service_id")
    _add_execution_args(run_p)
    run_p.set_defaults(func=cmd_run)

    picker_p = sub.add_parser("picker", help="Choose a service from a searchable list, then run it")
    _add_execution_args(picker_p)
    picker_p.set_defaults(func=cmd_picker)

    list_p = sub.add_parser("list", help="List available services")
    list_p.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
