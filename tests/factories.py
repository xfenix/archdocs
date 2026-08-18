import dataclasses
import pathlib
import random
import typing

import faker
from polyfactory.factories import DataclassFactory

from archdocs.main import SettingsForArchdocs


# Generated data is reproducible on purpose: one seed for the whole suite, so a value that
# reddens a test on one machine reddens it on the next one and in the pipeline. The generators
# are instances rather than the global `random` and `Faker.seed`, which every xdist worker
# would otherwise share with hypothesis and with each other.
GENERATOR_SEED: typing.Final = 20_260_818
# The manifest lookup climbs out of any root inside `tests/` and reaches the fixture charts, so
# a bare service node is asked for by a directory name nothing here has.
WITHOUT_MANIFESTS: typing.Final = "there-are-no-manifests-here"
_VALUE_GENERATOR: typing.Final = random.Random(GENERATOR_SEED)
_TEXT_GENERATOR: typing.Final = faker.Faker()
_TEXT_GENERATOR.seed_instance(GENERATOR_SEED)
_SECRET_LENGTH: typing.Final = 16
# Requests and limits are drawn from bands that cannot overlap, and so are the autoscaler
# bounds: a chart asking for more than it is allowed is not a chart anybody writes.
_SMALL_AMOUNTS: typing.Final = (1, 499)
_LARGE_AMOUNTS: typing.Final = (500, 999)
_FEW_REPLICAS: typing.Final = (1, 9)
_MANY_REPLICAS: typing.Final = (10, 99)
_LISTEN_PORTS: typing.Final = (1024, 65_535)
_UTILIZATION_PERCENTS: typing.Final = (1, 100)


@typing.final
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ServiceConnections:
    """Everything a service's own code says about its neighbours: hosts, names, credentials."""

    service_name: str
    user_name: str
    user_password: str
    database_host: str
    database_name: str
    broker_host: str
    consumed_topic: str
    produced_topic: str
    api_host: str
    listen_port: int


@typing.final
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ChartBlueprint:
    """Everything a chart says about the deployment, before it becomes yaml on disk."""

    chart_name: str
    ingress_host: str
    config_map_name: str
    secret_name: str
    secret_value: str
    storage_size: str
    requested_cpu: str
    limited_cpu: str
    requested_memory: str
    limited_memory: str
    replica_count: int
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: int
    service_port: int


def generate_name_part() -> str:
    return _TEXT_GENERATOR.word().lower()


def generate_number(number_band: tuple[int, int], /) -> int:
    return _VALUE_GENERATOR.randint(*number_band)


def render_amount(number_band: tuple[int, int], amount_unit: str, /) -> str:
    return f"{generate_number(number_band)}{amount_unit}"


def render_service_name() -> str:
    return f"{generate_name_part()}-{generate_name_part()}-svc"


# A leaked secret is what the page is searched for, so it may not look like anything else on
# it: a fixed prefix and a random tail no diagram word can spell.
def render_secret_value() -> str:
    return f"leaked-{_TEXT_GENERATOR.password(_SECRET_LENGTH, special_chars=False)}"


# The field providers are named after the fields they fill — that is how polyfactory binds
# them — so this module is a declaration of test data and not a module of functions.
@typing.final
class ServiceConnectionsFactory(DataclassFactory[ServiceConnections]):
    __random__ = _VALUE_GENERATOR
    __faker__ = _TEXT_GENERATOR

    @classmethod
    def service_name(cls) -> str:
        return render_service_name()

    @classmethod
    def user_name(cls) -> str:
        return f"{generate_name_part()}-user"

    @classmethod
    def user_password(cls) -> str:
        return render_secret_value()

    @classmethod
    def database_host(cls) -> str:
        return f"{generate_name_part()}-primary.internal"

    @classmethod
    def database_name(cls) -> str:
        return generate_name_part()

    @classmethod
    def broker_host(cls) -> str:
        return f"{generate_name_part()}-broker.internal"

    @classmethod
    def consumed_topic(cls) -> str:
        return f"{generate_name_part()}-commands"

    @classmethod
    def produced_topic(cls) -> str:
        return f"{generate_name_part()}-events"

    @classmethod
    def api_host(cls) -> str:
        return f"{generate_name_part()}-api.example.com"

    @classmethod
    def listen_port(cls) -> int:
        return generate_number(_LISTEN_PORTS)


@typing.final
class ChartBlueprintFactory(DataclassFactory[ChartBlueprint]):
    __random__ = _VALUE_GENERATOR
    __faker__ = _TEXT_GENERATOR

    @classmethod
    def chart_name(cls) -> str:
        return f"{generate_name_part()}-chart"

    @classmethod
    def ingress_host(cls) -> str:
        return f"{generate_name_part()}.example.com"

    @classmethod
    def config_map_name(cls) -> str:
        return f"{generate_name_part()}-config"

    @classmethod
    def secret_name(cls) -> str:
        return f"{generate_name_part()}-secrets"

    @classmethod
    def secret_value(cls) -> str:
        return render_secret_value()

    @classmethod
    def storage_size(cls) -> str:
        return render_amount(_SMALL_AMOUNTS, "Gi")

    @classmethod
    def requested_cpu(cls) -> str:
        return render_amount(_SMALL_AMOUNTS, "m")

    @classmethod
    def limited_cpu(cls) -> str:
        return render_amount(_LARGE_AMOUNTS, "m")

    @classmethod
    def requested_memory(cls) -> str:
        return render_amount(_SMALL_AMOUNTS, "Mi")

    @classmethod
    def limited_memory(cls) -> str:
        return render_amount(_LARGE_AMOUNTS, "Mi")

    @classmethod
    def replica_count(cls) -> int:
        return generate_number(_FEW_REPLICAS)

    @classmethod
    def min_replicas(cls) -> int:
        return generate_number(_FEW_REPLICAS)

    @classmethod
    def max_replicas(cls) -> int:
        return generate_number(_MANY_REPLICAS)

    @classmethod
    def target_cpu_utilization(cls) -> int:
        return generate_number(_UTILIZATION_PERCENTS)

    @classmethod
    def service_port(cls) -> int:
        return generate_number(_LISTEN_PORTS)


# The manifests are off by default and asked for by name: every root inside `tests/` reaches
# the fixture charts, so a test that has not asked for a chart must not be given one.
@typing.final
class SettingsFactory(DataclassFactory[SettingsForArchdocs]):
    __random__ = _VALUE_GENERATOR
    __faker__ = _TEXT_GENERATOR

    @classmethod
    def root_dir(cls) -> pathlib.Path:
        return pathlib.Path()

    @classmethod
    def service_name(cls) -> str:
        return render_service_name()

    @classmethod
    def kubernetes_dir(cls) -> str:
        return WITHOUT_MANIFESTS
