import ast as py_ast
import dataclasses
import pathlib
import typing

from fastarch.mapping import MAPPING_OF_PARSERS_AND_DRAWERS


"""TODO:

redis, postgres
faststream, kafka, rabbitmq, nats brokers
fastapi, litestar support

parsers from settings.py typical configuration

parsers from helm chart/manifests vital k8s information

parsers from docker-compose.yml?
"""


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class FeaturesInSourceFinder:
    root_dir: str
    service_name: str

    def traverse_by_codebase(self) -> typing.Generator[py_ast.Module]:
        for one_path in pathlib.Path(self.root_dir).rglob("*.py"):
            yield py_ast.parse(one_path.read_text())

    def search_for_familiar_objects_in_file(self, one_src_file: pathlib.Path) -> {bool, bool}:
        raw_file_source: typing.Final = one_src_file.read_text()
        return "".join(
            [
                features_functions.render(self.service_name, features_functions.parse(raw_file_source))
                for features_functions in MAPPING_OF_PARSERS_AND_DRAWERS.values()
            ],
        ).strip()
