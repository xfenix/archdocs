import dataclasses
import functools
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
    service_node_id: str,
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
                    one_manifest_functions.render_diagram(service_node_id, one_parsed_manifest)
                    for one_manifest_functions, one_parsed_manifest in all_parsed_manifests
                ),
            ),
        ),
    )


def _render_unique_edge_lines(manifest_diagram: str, source_files_diagram: str, /) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            filter(None, (*manifest_diagram.split("\n"), *source_files_diagram.split("\n"))),
        ),
    )


def _render_external_client_definition(all_edge_lines: typing.Iterable[str], /) -> str:
    # The node carries a slash in its title, which is not a legal mermaid id, so the edges
    # reference a sanitised id and the title arrives here, once, as a quoted label.
    if any(settings.EXTERNAL_CLIENT_NODE_ID in one_edge_line for one_edge_line in all_edge_lines):
        return mermaid_syntax.render_node_definition(
            settings.EXTERNAL_CLIENT_NODE_ID,
            settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
        )
    return ""


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
        full_result: typing.Final = self._render_every_diagram_line()
        self._cache.append(full_result)
        return full_result

    def _render_every_diagram_line(self) -> str:
        root_path: typing.Final = pathlib.Path(self.local_settings.root_dir).resolve()
        service_node_id: typing.Final = mermaid_syntax.render_service_node_id(self.local_settings.service_name)
        node_annotations, manifest_diagram = _render_manifest_features(
            service_node_id,
            root_path,
            self.local_settings.helm_chart_dir,
        )
        all_edge_lines: typing.Final = _render_unique_edge_lines(
            manifest_diagram,
            self._process_source_files(service_node_id, root_path),
        )
        return "\n".join(
            filter(
                None,
                (
                    mermaid_syntax.render_service_node_definition(self.local_settings.service_name, node_annotations),
                    _render_external_client_definition(all_edge_lines),
                    *all_edge_lines,
                ),
            ),
        )

    def _process_source_files(self, service_node_id: str, root_path: pathlib.Path, /) -> str:
        py_files: typing.Final = sorted(root_path.rglob(settings.FILES_SEARCH_PATTERN))
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            all_rendered_files: typing.Final = executor.map(
                functools.partial(self._process_one_file, service_node_id),
                py_files,
            )
            return "\n".join(filter(None, all_rendered_files))

    def _process_one_file(self, service_node_id: str, one_src_file: pathlib.Path, /) -> str:
        raw_file_source: typing.Final = one_src_file.read_text()
        return "\n".join(
            filter(
                None,
                (
                    one_feature_functions.render_diagram(
                        service_node_id,
                        one_feature_functions.parse_source(raw_file_source),
                    )
                    for one_feature_functions in MAPPING_OF_PARSERS_AND_RENDERERS.values()
                ),
            ),
        )
