import dataclasses
import pathlib
import typing
from concurrent import futures

from fastarch import mermaid_syntax, settings
from fastarch.mapping import MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS, MAPPING_OF_PARSERS_AND_RENDERERS


"""TODO:

parsers from settings.py typical configuration
parsers from docker-compose.yml?
"""


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SettingsForFastarch:
    root_dir: str | pathlib.Path
    service_name: str
    helm_chart_dir: str | pathlib.Path | None = None


def _render_manifest_features(
    root_path: pathlib.Path,
    configured_manifest_dir: str | pathlib.Path | None,
    /,
) -> tuple[tuple[str, ...], str]:
    all_parsed_manifests: typing.Final = [
        (
            one_manifest_functions,
            one_manifest_functions.parse_manifests(
                one_manifest_functions.read_source(root_path, configured_manifest_dir),
            ),
        )
        for one_manifest_functions in MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS.values()
    ]
    return (
        tuple(
            one_annotation
            for one_manifest_functions, one_parsed_manifest in all_parsed_manifests
            for one_annotation in one_manifest_functions.render_node_annotations(one_parsed_manifest)
        ),
        "\n".join(
            filter(
                None,
                (
                    one_manifest_functions.render_diagram(one_parsed_manifest)
                    for one_manifest_functions, one_parsed_manifest in all_parsed_manifests
                ),
            ),
        ),
    )


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
        root_path: typing.Final = pathlib.Path(self.local_settings.root_dir).resolve()
        node_annotations, manifest_diagram = _render_manifest_features(root_path, self.local_settings.helm_chart_dir)
        all_diagram_lines: typing.Final = [
            mermaid_syntax.render_service_node_definition(self.local_settings.service_name, node_annotations),
            *manifest_diagram.split("\n"),
            *self._process_source_files(root_path).split("\n"),
        ]
        full_result: typing.Final = "\n".join(dict.fromkeys(filter(None, all_diagram_lines)))
        self._cache.append(full_result)
        return full_result

    def _process_source_files(self, root_path: pathlib.Path) -> str:
        py_files: typing.Final = sorted(root_path.rglob(settings.FILES_SEARCH_PATTERN))
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            return "\n".join(filter(None, executor.map(self._process_one_file, py_files)))

    def _process_one_file(self, one_src_file: pathlib.Path) -> str:
        raw_file_source: typing.Final = one_src_file.read_text()
        return "\n".join(
            filter(
                None,
                (
                    one_feature_functions.render_diagram(
                        one_feature_functions.parse_source(raw_file_source),
                    )
                    for one_feature_functions in MAPPING_OF_PARSERS_AND_RENDERERS.values()
                ),
            ),
        )
