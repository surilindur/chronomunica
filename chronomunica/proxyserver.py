from flask import Flask, Response, request as incoming_request
from requests import request as request
from logging import info, exception
from typing import List, Dict

# from multiprocessing import Process
from threading import Thread


class ProxyServer:
    app: Flask
    urls: List[str]

    # process: Process
    thread: Thread

    protocol: str
    host: str
    port: int

    server_host: str
    server_port: int

    def __init__(self, config: Dict[str, str | int]) -> None:
        self.protocol = config["protocol"]
        self.host = config["proxy_host"]
        self.port = int(config["proxy_port"])
        self.server_host = config["upstream_host"]
        self.server_port = int(config["upstream_port"])
        self.urls = []

        self.app = Flask(__name__)
        target_base = f"{self.protocol}://{self.server_host}:{self.server_port}"

        @self.app.route("/", defaults={"path": ""}, methods=["GET", "HEAD", "OPTIONS"])
        @self.app.route("/<path:path>", methods=["GET", "HEAD", "OPTIONS"])
        def proxy(path) -> Response:
            try:
                url = f"{target_base}/{path}"
                self.urls.append(url)
                res = request(
                    method=incoming_request.method,
                    url=url,
                    data=incoming_request.data,
                    headers={
                        k: v for k, v in incoming_request.headers if k.lower() != "host"
                    },
                    cookies=incoming_request.cookies,
                    stream=True,
                    allow_redirects=False,
                )
                excluded_headers = [
                    "content-encoding",
                    "content-length",
                    "transfer-encoding",
                    "connection",
                ]
                headers = [
                    (k, v)
                    for k, v in res.raw.headers.items()
                    if k.lower() not in excluded_headers
                ]
                return Response(
                    response=res.iter_content(decode_unicode=True),
                    status=res.status_code,
                    headers=headers,
                )
            except Exception as ex:
                exception(ex)
                raise ex

        # self.process = Process(
        self.thread = Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port},
            daemon=True,
        )

    def start(self) -> None:
        local_addr: str = f"{self.protocol}://{self.host}:{self.port}"
        upstream_addr: str = f"{self.protocol}://{self.server_host}:{self.server_port}"
        info(f"Starting proxy server {local_addr} -> {upstream_addr}")
        self.thread.start()
        # self.process.start()

    def stop(self) -> None:
        info("Terminating proxy server")
        # self.process.kill()
        self.thread.join()
        info("Terminated proxy server")

    def reset(self) -> List[str]:
        urls = list(u for u in self.urls)
        self.urls.clear()
        return urls
