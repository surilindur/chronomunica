from logging import info, debug, error, exception
from typing import Any, List, Dict, Set
from threading import Thread
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPResponse
from urllib.error import HTTPError
from urllib.request import Request, urlopen


IGNORE_HEADERS: Set[str] = set(
    (
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    )
)


class ProxyServer:
    urls: List[str]
    thread: Thread
    server: ThreadingHTTPServer

    def __init__(self, config: Dict[str, str | int]) -> None:
        host: str = config["proxy_host"]
        port: int = int(config["proxy_port"])
        upstream_host: str = config["upstream_host"]
        upstream_port: int = int(config["upstream_port"])
        protocol: str = "http"

        proxied_urls: List[str] = []
        self.urls = proxied_urls

        listen_base = f"{protocol}://{host}:{port}"
        proxy_base = f"{protocol}://{upstream_host}:{upstream_port}"

        info(f"Proxy server: <{listen_base}> to <{proxy_base}>")

        class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
            def proxy_request(self) -> None:
                try:
                    target_url = f"{proxy_base}{self.path}"
                    proxied_urls.append(target_url)
                    proxied_headers = {
                        k: v for k, v in self.headers.items() if k.lower() != "host"
                    }
                    request: Request = Request(
                        url=target_url,
                        headers=proxied_headers,
                        method=self.command,
                    )
                    response: HTTPResponse = urlopen(request)
                    self.send_response(code=response.status)
                    for k, v in response.headers.items():
                        if k.lower() not in IGNORE_HEADERS:
                            self.send_header(
                                k,
                                v.replace(proxy_base, listen_base)
                                if isinstance(v, str) and proxy_base in v
                                else v,
                            )
                    self.end_headers()
                    if response.chunked and response.chunk_left:
                        while response.chunk_left:
                            self.wfile.write(
                                response.read(response.chunk_left)
                                .decode()
                                .replace(proxy_base, listen_base)
                                .encode()
                            )
                    else:
                        self.wfile.write(
                            response.read()
                            .decode()
                            .replace(proxy_base, listen_base)
                            .encode()
                        )
                except HTTPError as ex:
                    self.send_error(ex.code)
                except ConnectionResetError as ex:
                    self.send_error(HTTPStatus.BAD_GATEWAY.value)
                except Exception as ex:
                    exception(ex)
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR.value)

            def send_error(
                self, code: int, message: str | None = None, explain: str | None = None
            ) -> None:
                try:
                    return super().send_error(code, message, explain)
                except Exception as ex:
                    exception(ex)

            def do_GET(self) -> None:
                self.proxy_request()

            def do_HEAD(self) -> None:
                self.proxy_request()

            def do_OPTIONS(self) -> None:
                self.proxy_request()

            def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
                debug(f"Proxy {code: >3} {self.command: <7} {self.path}")

            def log_message(self, format: str, *args: Any) -> None:
                debug(format, *args)

            def log_error(self, format: str, *args: Any) -> None:
                error("{}".format(args[0], f"{proxy_base}{self.path}"))

        self.server = ThreadingHTTPServer((host, port), ProxyHTTPRequestHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        info("Starting proxy server")
        self.thread.start()

    def stop(self) -> None:
        info("Shutting down proxy server")
        self.server.shutdown()
        self.thread.join()

    def reset(self) -> List[str]:
        urls = list(u for u in self.urls)
        self.urls.clear()
        return urls
