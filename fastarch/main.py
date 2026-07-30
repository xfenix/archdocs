import dataclasses
import functools
import pathlib
import typing
from concurrent import futures

from fastarch import diagram_model, mermaid_syntax, settings
from fastarch.mapping import (
    MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS,
    MAPPING_OF_PARSERS_AND_RENDERERS,
    ManifestFeatureFunctions,
)


"""TODO:

parsers from settings.py typical configuration
parsers from docker-compose.yml?
"""


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SettingsForFastarch:
    root_dir: str | pathlib.Path
    service_name: str
    kubernetes_dir: str | pathlib.Path | None = None


type _ParsedManifests = tuple[tuple[ManifestFeatureFunctions, typing.Any], ...]


def _parse_every_manifest(
    root_path: pathlib.Path,
    configured_manifest_dir: str | pathlib.Path | None,
    /,
) -> _ParsedManifests:
    return tuple(
        (
            one_manifest_functions,
            one_manifest_functions.parse_manifests(
                one_manifest_functions.read_source(root_path, configured_manifest_dir),
            ),
        )
        for one_manifest_functions in MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS.values()
    )


def _render_manifest_annotations(all_parsed_manifests: _ParsedManifests, /) -> tuple[str, ...]:
    return tuple(
        one_annotation
        for one_manifest_functions, one_parsed_manifest in all_parsed_manifests
        for one_annotation in one_manifest_functions.render_node_annotations(one_parsed_manifest)
    )


def _render_manifest_edges(
    service_node: diagram_model.DiagramNode,
    all_parsed_manifests: _ParsedManifests,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    return tuple(
        one_edge
        for one_manifest_functions, one_parsed_manifest in all_parsed_manifests
        for one_edge in one_manifest_functions.render_diagram(service_node, one_parsed_manifest)
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
        full_result: typing.Final = self._render_every_diagram_line()
        self._cache.append(full_result)
        return full_result

    def _render_every_diagram_line(self) -> str:
        root_path: typing.Final = pathlib.Path(self.local_settings.root_dir).resolve()
        all_parsed_manifests: typing.Final = _parse_every_manifest(root_path, self.local_settings.kubernetes_dir)
        service_node: typing.Final = diagram_model.build_service_node(
            self.local_settings.service_name,
            _render_manifest_annotations(all_parsed_manifests),
        )
        all_edges: typing.Final = (
            *_render_manifest_edges(service_node, all_parsed_manifests),
            *self._process_source_files(service_node, root_path),
        )
        return mermaid_syntax.MermaidDiagram(service_node=service_node, all_edges=all_edges).render_every_line()

    def _process_source_files(
        self,
        service_node: diagram_model.DiagramNode,
        root_path: pathlib.Path,
        /,
    ) -> tuple[diagram_model.DiagramEdge, ...]:
        py_files: typing.Final = sorted(root_path.rglob(settings.FILES_SEARCH_PATTERN))
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            all_rendered_files: typing.Final = executor.map(
                functools.partial(self._process_one_file, service_node),
                py_files,
            )
            return tuple(one_edge for one_file_edges in all_rendered_files for one_edge in one_file_edges)

    def _process_one_file(
        self,
        service_node: diagram_model.DiagramNode,
        one_src_file: pathlib.Path,
        /,
    ) -> tuple[diagram_model.DiagramEdge, ...]:
        raw_file_source: typing.Final = one_src_file.read_text()
        return tuple(
            one_edge
            for one_feature_functions in MAPPING_OF_PARSERS_AND_RENDERERS.values()
            for one_edge in one_feature_functions.render_diagram(
                service_node,
                one_feature_functions.parse_source(raw_file_source),
            )
        )
