from argparse import ArgumentParser, Namespace
from logging import basicConfig, info, INFO, ERROR, DEBUG
from typing import Dict, Optional
from pathlib import Path
from sys import stdout

log_levels: Dict[str, int] = {"info": INFO, "error": ERROR, "debug": DEBUG}


class ArgumentNamespace(Namespace):
    log_level: str
    log_file: Optional[Path]
    experiment: Path | None
    plot: Path | None


def parse_path(path: str) -> Path:
    return Path(path.removeprefix("file://")).resolve()


def setup_logging(level: str, path: Optional[Path]) -> None:
    log_target_args = (
        {"filename": path, "filemode": "w", "encoding": "utf-8"}
        if path
        else {"stream": stdout}
    )
    basicConfig(
        **log_target_args,
        format="{asctime} | {levelname: <9} | {module}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        level=log_levels[level],
    )
    info(f"Logging setup finished, logging at {level} level")


def parse_arguments() -> ArgumentNamespace:
    argument_parser = ArgumentParser(
        prog="chronomunica",
        description="Minimal benchmark runner for Comunica clients",
        epilog="Please feel free to report any issues on GitHub",
        allow_abbrev=False,
    )

    argument_parser.add_argument(
        "--log-level", choices=log_levels.keys(), default="info"
    )

    argument_parser.add_argument("--log-file", required=False, type=Path)

    group = argument_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--experiment", type=Path)
    group.add_argument("--plot", type=Path)

    args = argument_parser.parse_args(namespace=ArgumentNamespace)

    setup_logging(level=args.log_level, path=args.log_file)

    return args
