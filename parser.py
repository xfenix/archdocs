import ast as py_ast
import dataclasses
import pathlib
import typing

from features.base import MAP_OF_FEATURES


""" Possible features

redis, postgres
faststream, kafka, rabbitmq, nats brokers
fastapi, litestar support

Parsing from settings.py typical configuration

Parsing from helm chart/manifests vital k8s information

Parsing from docker-compose.yml?
"""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class FeaturesInSourceFinder:
    root_dir: str

    def traverse_by_codebase(self) -> typing.Generator[py_ast.Module]:
        for one_path in pathlib.Path(self.root_dir).rglob("*.py"):
            yield py_ast.parse(one_path.read_text())

    def search_for_familiar_objects_in_file(self, one_src_file: pathlib.Path) -> {bool, bool}:
        result_map: dict[int, typing.Any] = {}
        raw_src: typing.Final = one_src_file.read_text()
        for one_search_type, run_search_for_this_type in MAP_OF_FEATURES.items():
            result_map[one_search_type] = run_search_for_this_type(raw_src)
        return result_map
