from json import loads
from pathlib import Path
from logging import info, warn, error
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse, ParseResult
from math import sqrt, ceil
from matplotlib.cm import get_cmap
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import figure
from matplotlib.colors import Colormap


# Time is recorded in nanoseconds
TIME_DIVISOR: int = 1000 * 1000 * 1000
IMAGE_EXTENSION: str = "svg"


class ChronomunicaResult:
    config: str
    query: str
    result_count: int
    result_hash: str
    max_time: float
    result_times: List[float]
    other_times: List[float]

    def __init__(self, config: str, query: str, data: List[Dict[str, Any]]) -> None:
        self.config = self.config_uri_to_id(config)
        self.query = self.query_uri_to_id(query)
        self.result_hash = None
        self.result_count = 0
        self.other_times = []
        self.result_times = []
        for rep in data:
            if not self.result_hash:
                self.result_hash = rep["result_hash"]
                self.result_count = int(rep["result_count"])
            else:
                assert (
                    self.result_hash == rep["result_hash"]
                ), f"Inconsistent results for {self.query} with {self.config}"
            if "other_output" in rep:
                other_times = list(
                    int(k) / TIME_DIVISOR for k in rep["other_output"].keys()
                )
                self.other_times = self.average_lists(self.other_times, other_times)
            if "result_bindings" in rep:
                result_times = list(
                    int(k) / TIME_DIVISOR for k in rep["result_bindings"].keys()
                )
                self.result_times = self.average_lists(self.result_times, result_times)
            else:
                warn(f"No results for {self.query} with {self.config}")
        self.max_time = max(
            self.result_times[-1] if self.result_times else 0,
            self.other_times[-1] if self.other_times else 0,
        )

    def average_lists(self, a: List[float], b: List[float]) -> List[float]:
        existing_length: int = min(len(a), len(b))
        for i in range(0, existing_length):
            new_value: float = b.pop(0)
            prev_value: float = a[i - 1] if i > 0 else a[i]
            a[i] = max(new_value, (a[i] + new_value) / 2, a[i], prev_value)
        while len(b):
            last_value: float = a[-1] if a else -1
            a.append(max(b.pop(0), last_value))
        return a

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


class ChronomunicaResults:
    path: Path
    results: List[ChronomunicaResult]

    # time is recorded in nanoseconds
    time_divisor: int = 0

    def __init__(self, path: Path) -> None:
        self.path = path
        with open(path, "r") as result_file:
            self.data = loads(result_file.read())
        self.results = []
        for config, config_data in self.data.items():
            for query, query_data in config_data.items():
                try:
                    self.results.append(
                        ChronomunicaResult(
                            config=config,
                            query=query,
                            data=query_data,
                        )
                    )
                except Exception as ex:
                    error(ex)

    def make_diefficiency_y_axis(self, length: int) -> List[int]:
        return list(range(1, length + 1))

    def calculate_ticks(self, max_value: int) -> int:
        if max_value < 20:
            return 1
        elif max_value < 200:
            return 10
        elif max_value < 2000:
            return 100

    def calculate_rows_cols(self, subplots: int) -> Tuple[int, int]:
        plot_cols: int = ceil(sqrt(subplots))
        plot_rows: int = ceil(subplots / plot_cols)
        return plot_rows, plot_cols

    def plot_diefficiency(self, suffix: str = IMAGE_EXTENSION) -> None:
        fig: Figure = figure(dpi=300)
        output_path: Path = self.path.parent.joinpath(
            f"{self.path.stem}-diefficiency.{suffix}"
        )
        subplot_index: int = 0
        fig_handles = []
        fig_labels = []
        cmap: Colormap = get_cmap("tab10")
        unique_configs: List[str] = list(sorted(set(r.config for r in self.results)))
        config_color: Dict[str, Tuple[float, float, float, float]] = {
            unique_configs[i]: cmap(i) for i in range(0, len(unique_configs))
        }
        results_by_query: Dict[str, List[ChronomunicaResult]] = {}
        for result in self.results:
            if result.query not in results_by_query:
                results_by_query[result.query] = []
            results_by_query[result.query].append(result)
        rows, cols = self.calculate_rows_cols(len(results_by_query))
        info(f"Plotting into {cols} x {rows} grid")
        fig.set_size_inches(w=cols * 5, h=rows * 4)
        for query, results in results_by_query.items():
            subplot_index += 1
            ax: Axes = fig.add_subplot(rows, cols, subplot_index)
            ax.grid(axis="x", color="0.95", which="major")
            ax.set_xlabel(xlabel="time (s)")
            ax.set_ylabel("results")
            ax.set_title(query)
            query_max_time: float = 0.0
            for result in sorted(results, key=lambda k: f"{k.query} {k.config}"):
                query_max_time = max(query_max_time, result.max_time)
                plot_args: Dict[str, Any] = {
                    "color": config_color[result.config],
                    "alpha": 0.8,
                    "lw": 1,
                }
                if result.result_count == 1:
                    ax.plot(
                        result.result_times[0],
                        1,
                        marker=".",
                        label=result.config,
                        **plot_args,
                    )
                else:
                    ax.step(
                        x=result.result_times,
                        y=self.make_diefficiency_y_axis(result.result_count),
                        where="post",
                        label=result.config,
                        **plot_args,
                    )
                if result.other_times:
                    for t in result.other_times:
                        ax.axvline(x=t, ls=":", **plot_args)
            ax.set_xbound(lower=0, upper=int(ceil(query_max_time + 0.5)))
            handles, labels = ax.get_legend_handles_labels()
            if len(handles) > len(fig_handles) and len(labels) > len(fig_labels):
                fig_labels = labels
                fig_handles = handles
        fig.legend(
            handles=fig_handles,
            labels=fig_labels,
            bbox_to_anchor=(0.5, 1.05),
            loc="upper center",
            ncols=len(fig_labels),
        )
        fig.tight_layout(pad=1, h_pad=1, w_pad=1)
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
