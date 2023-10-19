from json import loads
from pathlib import Path
from logging import info
from typing import Dict, Any, List
from urllib.parse import urlparse, ParseResult
from math import sqrt, ceil
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import figure


class ChronomunicaResults:
    path: Path
    data: Dict[str, Dict[str, List[Dict[str, Any]]]]

    # time is recorded in nanoseconds
    time_divisor: int = 1000 * 1000 * 1000

    def __init__(self, path: Path) -> None:
        self.path = path
        with open(path, "r") as result_file:
            self.data = loads(result_file.read())

    def config_uri_to_id(self, uri: str) -> str:
        config_parsed: ParseResult = urlparse(uri)
        return (
            config_parsed.path.split("/")[-1]
            .removesuffix(".json")
            .replace("-", " ")
            .removeprefix("config default ")
            .capitalize()
        )

    def query_uri_to_id(self, uri: str) -> str:
        query_parsed: ParseResult = urlparse(uri)
        id_base: str = " ".join(
            s.capitalize()
            for s in query_parsed.path.split("/")[-1].removesuffix(".sparql").split("-")
        )
        query_id: str = f"{id_base}.{query_parsed.fragment}"
        return query_id

    def result_times(self) -> Dict[str, Dict[str, List[float]]]:
        result_times: Dict[str, Dict[str, List[float]]] = {}
        for config, config_data in self.data.items():
            config_id: str = self.config_uri_to_id(config)
            for query, query_data in config_data.items():
                query_id: str = self.query_uri_to_id(query)
                if query_id not in result_times:
                    result_times[query_id] = {}
                query_data = list(r for r in query_data if "result_count" in r)
                required_count: int = max(int(r["result_count"]) for r in query_data)
                query_data = list(
                    r for r in query_data if int(r["result_count"]) == required_count
                )
                average_arrivals: List[float] = []
                for repetition in query_data:
                    times: List[float] = list(
                        int(k) / self.time_divisor
                        for k in repetition["result_bindings"].keys()
                    )
                    if len(average_arrivals) < required_count:
                        average_arrivals = times
                    else:
                        for i in range(0, required_count):
                            average_arrivals[i] = (average_arrivals[i] + times[i]) / 2
                result_times[query_id][config_id] = average_arrivals
        return result_times

    def make_diefficiency_y_axis(length: int) -> List[int]:
        return list(range(1, length + 1))

    def plot_diefficiency(self, suffix: str = "png") -> None:
        fig: Figure = figure(dpi=600)
        output_path: Path = self.path.parent.joinpath(f"{self.path.stem}.{suffix}")
        result_times = self.result_times()
        total_plots: int = len(result_times)
        plot_cols: int = ceil(sqrt(total_plots))
        plot_rows: int = ceil(total_plots / plot_cols)
        fig.set_size_inches(plot_cols * 6, plot_rows * 6)
        info(f"Plotting into {plot_cols} x {plot_rows} grid")
        subplot_index: int = 1
        for query, query_data in result_times.items():
            ax: Axes = fig.add_subplot(plot_rows, plot_cols, subplot_index)
            for config, arrival_times in query_data.items():
                ax.step(
                    x=arrival_times,
                    y=self.make_diefficiency_y_axis(len(arrival_times)),
                    where="post",
                    label=config,
                )
            ax.grid(axis="x", color="0.95", which="major")
            ax.set_xbound(lower=0, upper=ceil(max(arrival_times) + 0.5))
            ax.set_xlabel(xlabel="time (s)")
            ax.set_ylabel("results")
            ax.set_title(query)
            handles, labels = ax.get_legend_handles_labels()
            subplot_index += 1
        fig.legend(
            handles=handles,
            labels=labels,
            bbox_to_anchor=(0.5, 1),
            loc="upper center",
            ncols=plot_cols,
        )
        fig.savefig(fname=output_path, transparent=False, bbox_inches="tight")


def plot_chronomunica_results(path: Path) -> None:
    info(f"Visualizing results from {path}")
    results: ChronomunicaResults = ChronomunicaResults(path)
    results.plot_diefficiency()
    info("Finished visualization")


def plot_jbr_results(path: Path) -> None:
    pass


def plot_results(path: Path) -> None:
    match path.suffix:
        case ".csv":
            plot_jbr_results(path)
        case ".json":
            plot_chronomunica_results(path)
        case _:
            info(f"Unknown result type {path}")
