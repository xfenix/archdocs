import dataclasses
import pathlib
import typing

from hypothesis import strategies as st

from tests import factories


# One source file per project, every selected technology appended to it: a project assembled
# from leftovers of the previous example would prove nothing, and a technology that only works
# when it is alone in a file is a technology that does not work.
SOURCE_FILE_NAME: typing.Final = "main.py"
VALUES_FILE_NAME: typing.Final = "values.yaml"
_CHART_FILE_NAME: typing.Final = "Chart.yaml"
_CHART_TEMPLATE: typing.Final = "apiVersion: v2\nname: {chart_name}\nversion: 0.1.0\n"
# Requests, limits, hosts and the autoscaler as a chart writes them, plus one value no chart
# should ever show: `secretValues` is what the leak test looks for on the finished page.
_VALUES_TEMPLATE: typing.Final = """replicaCount: {replica_count}

service:
  type: ClusterIP
  port: {service_port}

ingress:
  enabled: true
  hosts:
    - host: {ingress_host}
  tls:
    - secretName: {ingress_host}-tls

autoscaling:
  enabled: true
  minReplicas: {min_replicas}
  maxReplicas: {max_replicas}
  targetCPUUtilizationPercentage: {target_cpu_utilization}

resources:
  requests:
    cpu: {requested_cpu}
    memory: {requested_memory}
  limits:
    cpu: {limited_cpu}
    memory: {limited_memory}

envFrom:
  - configMapRef:
      name: {config_map_name}
  - secretRef:
      name: {secret_name}

persistence:
  enabled: true
  size: {storage_size}

secretValues:
  databasePassword: {secret_value}
"""


@typing.final
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class OneTechnology:
    """A technology as a project shows it: the code it is written with and the arrow it earns."""

    technology_name: str
    source_template: str
    expected_mark_template: str


ALL_TECHNOLOGIES: typing.Final = (
    OneTechnology(
        technology_name="http_api",
        source_template=(
            "import fastapi\n\n\n"
            "api_router = fastapi.APIRouter()\n\n\n"
            '@api_router.get("/orders/")\n'
            "async def read_orders() -> list:\n"
            "    return []\n"
        ),
        expected_mark_template='|"REST (get)"|',
    ),
    OneTechnology(
        technology_name="http_clients",
        source_template=(
            "import httpx\n\n\n"
            'payments_client = httpx.AsyncClient(base_url="https://{user_name}:{user_password}@{api_host}")\n'
        ),
        expected_mark_template='External_API["External API"]',
    ),
    OneTechnology(
        technology_name="sqlalchemy",
        source_template=(
            "from sqlalchemy import create_engine\n\n\n"
            "orders_engine = create_engine(\n"
            '    "postgresql+psycopg://{user_name}:{user_password}@{database_host}:5432/{database_name}",\n'
            ")\n"
        ),
        expected_mark_template='postgresql_psycopgdb["postgresql+psycopg"]',
    ),
    OneTechnology(
        technology_name="redis_cache",
        source_template='import redis\n\n\ncache_client = redis.Redis(host="{database_host}")\n',
        expected_mark_template='redisdb["redis"]',
    ),
    OneTechnology(
        technology_name="messaging_queue",
        source_template=(
            "from faststream.rabbit import RabbitBroker\n\n\n"
            'rabbit_broker = RabbitBroker("amqp://{user_name}:{user_password}@{broker_host}:5672/")\n\n\n'
            '@rabbit_broker.subscriber("{consumed_topic}")\n'
            "async def handle_command(one_command: dict) -> None: ...\n\n\n"
            '@rabbit_broker.publisher("{produced_topic}")\n'
            "async def publish_event(one_event: dict) -> dict:\n"
            "    return one_event\n"
        ),
        expected_mark_template='rabbit --> |"{consumed_topic}"|',
    ),
    OneTechnology(
        technology_name="task_queues",
        source_template=(
            "import celery\n\n\n"
            'tasks_app = celery.Celery(broker="amqp://{user_name}:{user_password}@{broker_host}:5672//")\n\n\n'
            "@tasks_app.task\n"
            "def send_receipt(order_id: int) -> None: ...\n"
        ),
        expected_mark_template='|"Tasks (celery, rabbitmq)"|',
    ),
    OneTechnology(
        technology_name="app_servers",
        source_template='import uvicorn\n\n\nuvicorn.run("src.main:app", port={listen_port})\n',
        expected_mark_template='|"Served by uvicorn, port {listen_port}"|',
    ),
)
# Zero technologies is a project too: a service nobody wired to anything still has to be drawn.
TECHNOLOGY_SUBSET_STRATEGY: typing.Final = st.lists(
    st.sampled_from(ALL_TECHNOLOGIES),
    unique_by=lambda one_technology: one_technology.technology_name,
)


def render_expected_marks(
    all_technologies: typing.Iterable[OneTechnology],
    service_connections: factories.ServiceConnections,
    /,
) -> tuple[str, ...]:
    return tuple(
        one_technology.expected_mark_template.format(**dataclasses.asdict(service_connections))
        for one_technology in all_technologies
    )


def write_service_sources(
    project_path: pathlib.Path,
    all_technologies: typing.Iterable[OneTechnology],
    service_connections: factories.ServiceConnections,
    /,
) -> pathlib.Path:
    (project_path / SOURCE_FILE_NAME).write_text(
        "\n".join(
            one_technology.source_template.format(**dataclasses.asdict(service_connections))
            for one_technology in all_technologies
        ),
    )
    return project_path


def write_generated_chart(chart_path: pathlib.Path, chart_blueprint: factories.ChartBlueprint, /) -> pathlib.Path:
    chart_path.mkdir(parents=True, exist_ok=True)
    (chart_path / _CHART_FILE_NAME).write_text(_CHART_TEMPLATE.format(**dataclasses.asdict(chart_blueprint)))
    (chart_path / VALUES_FILE_NAME).write_text(_VALUES_TEMPLATE.format(**dataclasses.asdict(chart_blueprint)))
    return chart_path
