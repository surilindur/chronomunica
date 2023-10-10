from argparse import ArgumentParser, Namespace
from logging import basicConfig, info, INFO, ERROR, DEBUG
from typing import Dict
from pathlib import Path

default_logfile: Path = Path("chronomunica.log").resolve()

log_levels: Dict[str, int] = {"info": INFO, "error": ERROR, "debug": DEBUG}


class ArgumentNamespace(Namespace):
    loglevel: int
    logfile: Path
    benchmark: Path | None
    plot: Path | None


def setup_logging(level: str, path: Path) -> None:
    basicConfig(
        filename=path,
        format="{asctime} | {levelname: <9} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        level=log_levels[level],
        filemode="a",
        encoding="utf-8",
    )
    info(f'Logging setup finished, logging {level} to "{path}"')


def parse_arguments() -> ArgumentNamespace:
    argument_parser = ArgumentParser(
        prog="chronomunica",
        description="Minimal benchmark runner for Comunica clients",
        epilog="Please feel free to report any issues on GitHub",
        allow_abbrev=False,
    )

    argument_parser.add_argument(
        "--loglevel", choices=log_levels.keys(), default="info"
    )
    argument_parser.add_argument("--logfile", default=default_logfile, type=Path)

    group = argument_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--benchmark", type=Path)
    group.add_argument("--plot", type=Path)

    args = argument_parser.parse_args(namespace=ArgumentNamespace)

    setup_logging(level=args.loglevel, path=args.logfile)

    return args
