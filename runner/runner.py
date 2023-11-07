from pathlib import Path
from logging import exception, info
from datetime import timedelta

from experiment.experiment import Experiment
from experiment.result import Result, save_result

from runner.queryengine import QueryEngine
from runner.proxyserver import ProxyServer


class ExperimentRunner:
    def __init__(self, manifest: Path) -> None:
        self.experiment: Experiment = Experiment(path=manifest)
        self.proxy_server: ProxyServer = ProxyServer(
            host=self.experiment.proxy_server_host,
            port=self.experiment.proxy_server_port,
            upstream_host=self.experiment.proxy_server_upstream_host,
            upstream_port=self.experiment.proxy_server_upstream_port,
        )
        self.query_engine: QueryEngine = QueryEngine(
            cwd=self.experiment.query_engine_cwd,
            bin=self.experiment.query_engine_bin,
            node=self.experiment.query_engine_node,
            env=self.experiment.query_engine_environment,
            context=self.experiment.query_engine_context,
        )

    def get_total_execution_count(self) -> int:
        executions_total: int = (
            len(self.experiment.query_strings)
            * len(self.experiment.configs)
            * self.experiment.replication
        )
        info(f"Executing a total of {executions_total} experiments")
        seconds = self.experiment.query_engine_timeout * executions_total
        days, remainder = divmod(seconds, 60 * 60 * 24)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        info(
            f"Maximum duration {days} days {hours} hours {minutes} minutes {seconds} seconds"
        )
        return executions_total

    def execute(self) -> None:
        exec_total: int = self.get_total_execution_count() - 1
        exec_done: int = 0
        query_timeout: timedelta = timedelta(
            seconds=self.experiment.query_engine_timeout
        )
        self.proxy_server.start()
        for query_id, query_string in self.experiment.query_strings.items():
            info(f"Executing query <{query_id}>")
            for config_path in self.experiment.configs:
                for i in range(0, self.experiment.replication):
                    info(f"Execute {exec_done} / {exec_total} <file://{config_path}>")
                    result: Result | None = self.execute_query(
                        query_id=query_id,
                        query_string=query_string,
                        config_path=config_path,
                        timeout=query_timeout,
                    )
                    if result:
                        info(f"Finished with {len(result.results)} results")
                        save_result(self.experiment.results, result)
                    exec_done += 1
        self.proxy_server.stop()

    def execute_query(
        self,
        query_id: str,
        query_string: str,
        config_path: Path,
        timeout: timedelta,
    ) -> Result | None:
        try:
            result: Result = self.query_engine.query_bindings(
                query_id=query_id,
                query_string=query_string,
                timeout=timeout,
                config_path=config_path,
            )
            result.urls = self.proxy_server.reset()
            return result
        except Exception as ex:
            exception(ex)
