from argparse import ArgumentParser, Namespace
from logging import basicConfig, info, INFO, ERROR, DEBUG
from typing import Dict
from pathlib import Path
from sys import stdout

log_levels: Dict[str, int] = {"info": INFO, "error": ERROR, "debug": DEBUG}


class ArgumentNamespace(Namespace):
    log_level: str
    log_file: Path | None
    experiment: Path | None
    plot: Path | None
    create: Path | None


def setup_logging(level: str, path: Path | None) -> None:
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
    parser = ArgumentParser(
        prog="chronomunica",
        description="Minimal benchmark runner for Comunica clients",
        epilog="Please feel free to report any issues on GitHub",
        allow_abbrev=False,
    )

    parser.add_argument("--log-level", choices=log_levels.keys(), default="info")

    parser.add_argument("--log-file", required=False, type=Path)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", type=Path, help="Create experiment manifest at path")
    group.add_argument("--experiment", type=Path, help="Path to an experiment manifest")
    group.add_argument("--plot", type=Path, help="Path to query result file to plot")

    args = parser.parse_args(namespace=ArgumentNamespace)

    setup_logging(level=args.log_level, path=args.log_file)

    return args
