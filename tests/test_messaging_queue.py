import pathlib
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page


# `from faststream import FastStream` says nothing about the broker: it used to name every
# broker faststream ships with, so a single rabbit application was drawn talking to kafka and
# nats too. Producers are the mirror case — the decorator is `publisher`, `producer` exists
# nowhere in faststream, so outgoing edges never appeared for real code.
_SERVICE_NAME: typing.Final = "mq-svc"
_INCOMING_RABBIT_EDGE: typing.Final = '    rabbit --> |"MQ"| mq_svc'
_OUTGOING_RABBIT_EDGE: typing.Final = '    mq_svc --> |"MQ"| rabbit'
_MQ_LABEL: typing.Final = '|"MQ"|'
_CONSUMER_SOURCE: typing.Final = """from faststream import FastStream
from faststream.rabbit import RabbitBroker

rabbit_broker = RabbitBroker("amqp://user:password@localhost:5672/")
faststream_app = FastStream(rabbit_broker)


@rabbit_broker.subscriber("commands")
async def handle_command(command: dict) -> None:
    ...
"""
_PUBLISHER_DECORATOR_SOURCE: typing.Final = """from faststream.rabbit import RabbitBroker

rabbit_broker = RabbitBroker("amqp://user:password@localhost:5672/")


@rabbit_broker.publisher("events")
async def publish_event(event: dict) -> dict:
    return event
"""
_PUBLISH_CALL_SOURCE: typing.Final = """from faststream.rabbit import RabbitBroker

rabbit_broker = RabbitBroker("amqp://user:password@localhost:5672/")


async def publish_event(event: dict) -> None:
    await rabbit_broker.publish(event, queue="events")
"""
_SOURCE_WITHOUT_MESSAGING: typing.Final = """import fastapi

app = fastapi.FastAPI()
"""


def _render_diagram(project_path: pathlib.Path, source_code: str, /) -> str:
    (project_path / "main.py").write_text(source_code)
    return extract_diagram(
        render_architecture_page(SettingsForFastarch(root_dir=project_path, service_name=_SERVICE_NAME)),
    )


def test_only_the_imported_broker_reaches_diagram(tmp_path: pathlib.Path) -> None:
    rendered_diagram: typing.Final = _render_diagram(tmp_path, _CONSUMER_SOURCE)
    assert _INCOMING_RABBIT_EDGE in rendered_diagram
    assert "kafka" not in rendered_diagram
    assert "nats" not in rendered_diagram


@pytest.mark.parametrize("source_code", [_PUBLISHER_DECORATOR_SOURCE, _PUBLISH_CALL_SOURCE])
def test_produced_messages_draw_outgoing_edge(tmp_path: pathlib.Path, source_code: str) -> None:
    rendered_diagram: typing.Final = _render_diagram(tmp_path, source_code)
    assert _OUTGOING_RABBIT_EDGE in rendered_diagram
    assert _INCOMING_RABBIT_EDGE not in rendered_diagram


def test_no_broker_without_faststream(tmp_path: pathlib.Path) -> None:
    assert _MQ_LABEL not in _render_diagram(tmp_path, _SOURCE_WITHOUT_MESSAGING)
