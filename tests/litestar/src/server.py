"""Granian entrypoint for the litestar example."""

import pathlib
import typing

import granian
from granian.constants import HTTPModes, Interfaces


CERTIFICATES_DIR: typing.Final = pathlib.Path("/etc/tls")


def run_application_server() -> None:
    """Serve the litestar application with granian."""
    granian.Granian(
        "tests.litestar.src.main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        http=HTTPModes.http2,
        workers=4,
        ssl_cert=CERTIFICATES_DIR / "tls.crt",
        ssl_key=CERTIFICATES_DIR / "tls.key",
    ).serve()


if __name__ == "__main__":
    run_application_server()
