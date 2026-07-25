import dataclasses
import pathlib
import typing
from concurrent import futures

from fastarch import settings
from fastarch.mapping import MAPPING_OF_PARSERS_AND_RENDERERS


"""TODO:

parsers from settings.py typical configuration
parsers from helm chart/manifests vital k8s information
parsers from docker-compose.yml?
"""


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SettingsForFastarch:
    root_dir: str | pathlib.Path
    service_name: str


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ArchitectureParserAndRenderer:
    local_settings: SettingsForFastarch
    _cache: list[str] = dataclasses.field(default_factory=list)

    def render_architecture_diagram(self) -> str:
        # "why you doesnt use functools.cache lol"
        # https://docs.astral.sh/ruff/rules/cached-instance-method/#cached-instance-method-b019
        if self._cache:
            return self._cache[0]
        py_files: typing.Final = list(
            pathlib.Path(self.local_settings.root_dir).resolve().rglob(settings.FILES_SEARCH_PATTERN),
        )
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            full_result: typing.Final = "\n".join(
                filter(None, executor.map(self._process_one_file, py_files)),
            )
        self._cache.append(full_result)
        return full_result

    def _process_one_file(self, one_src_file: pathlib.Path) -> str:
        raw_file_source: typing.Final = one_src_file.read_text()
        return "".join(
            one_feature_functions.render_diagram(
                self.local_settings.service_name,
                one_feature_functions.parse_source(raw_file_source),
            )
            for one_feature_functions in MAPPING_OF_PARSERS_AND_RENDERERS.values()
        ).strip()
