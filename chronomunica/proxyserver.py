from requests import request
from logging import info, debug, error
from typing import Any, List, Dict
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class ProxyServer:
    urls: List[str]
    thread: Thread
    server: ThreadingHTTPServer

    def __init__(self, config: Dict[str, str | int]) -> None:
        protocol: str = config["protocol"]
        host: str = config["proxy_host"]
        port: int = int(config["proxy_port"])
        upstream_host: str = config["upstream_host"]
        upstream_port: int = int(config["upstream_port"])

        proxied_urls: List[str] = []
        self.urls = proxied_urls

        listen_base = f"{protocol}://{host}:{port}"
        proxy_base = f"{protocol}://{upstream_host}:{upstream_port}"

        excluded_headers = set(
            (
                "content-encoding",
                "content-length",
                "transfer-encoding",
                "connection",
            )
        )

        info(f"Proxy server: {listen_base} -> {proxy_base}")

        class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
            def proxy_request(self) -> None:
                target_url = f"{proxy_base}{self.path}"
                proxied_urls.append(target_url)
                proxied_headers = {
                    k: v for k, v in self.headers.items() if k.lower() != "host"
                }
                res = request(
                    method=self.command,
                    url=target_url,
                    headers=proxied_headers,
                    stream=True,
                    allow_redirects=False,
                )
                self.send_response(code=res.status_code)
                for k, v in res.headers.items():
                    if k.lower() not in excluded_headers:
                        self.send_header(k, v)
                self.end_headers()
                for chunk in res.iter_content(decode_unicode=True):
                    self.wfile.write(chunk)

            def do_GET(self) -> None:
                self.proxy_request()

            def do_HEAD(self) -> None:
                self.proxy_request()

            def do_OPTIONS(self) -> None:
                self.proxy_request()

            def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
                debug(f"Proxy {code: >3} {self.command: <7} {self.path}")

            def log_message(self, format: str, *args: Any) -> None:
                debug(format.format(args))

            def log_error(self, format: str, *args: Any) -> None:
                error(format.format(args))

        self.server = ThreadingHTTPServer((host, port), ProxyHTTPRequestHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        info("Starting proxy server")
        self.thread.start()

    def stop(self) -> None:
        info("Shutting down proxy server")
        self.server.shutdown()
        # self.thread.join()

    def reset(self) -> List[str]:
        urls = list(u for u in self.urls)
        self.urls.clear()
        return urls
