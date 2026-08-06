import dataclasses
import functools
import pathlib
import typing
from concurrent import futures

from archdocs import diagram_model, mapping, mermaid_syntax, settings


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SettingsForArchdocs:
    root_dir: str | pathlib.Path
    service_name: str
    kubernetes_dir: str | pathlib.Path | None = None


type _ParsedManifests = tuple[tuple[mapping.ManifestFeatureFunctions[typing.Any], typing.Any], ...]


def _read_source_text(one_source_file: pathlib.Path, /) -> str:
    # The scanned tree is somebody's whole project, not a curated corpus: a source in a legacy
    # encoding, a symlink into nowhere or a file the process may not open costs that one file and
    # nothing else. Without this the page answers 500 instead of drawing the rest of the service.
    try:
        return one_source_file.read_text(errors="ignore")
    except OSError:
        return ""


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
        for one_manifest_functions in mapping.MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS.values()
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
        for one_edge in one_manifest_functions.render_edges(service_node, one_parsed_manifest)
    )


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ArchitectureParserAndRenderer:
    local_settings: SettingsForArchdocs
    # The cache is state, not identity: leaving it out of `__eq__` keeps the frozen dataclass
    # hashable, which a list field would otherwise take away.
    _rendered_diagram_cache: list[str] = dataclasses.field(default_factory=list, compare=False)

    def render_architecture_diagram(self) -> str:
        # "why you doesnt use functools.cache lol"
        # https://docs.astral.sh/ruff/rules/cached-instance-method/#cached-instance-method-b019
        if self._rendered_diagram_cache:
            return self._rendered_diagram_cache[0]
        rendered_diagram: typing.Final = self._render_every_diagram_line()
        self._rendered_diagram_cache.append(rendered_diagram)
        return rendered_diagram

    def _render_every_diagram_line(self) -> str:
        root_path: typing.Final = pathlib.Path(self.local_settings.root_dir).resolve()
        all_parsed_manifests: typing.Final = _parse_every_manifest(root_path, self.local_settings.kubernetes_dir)
        service_node: typing.Final = diagram_model.build_service_node(
            self.local_settings.service_name,
            _render_manifest_annotations(all_parsed_manifests),
        )
        all_edges: typing.Final = (
            *_render_manifest_edges(service_node, all_parsed_manifests),
            *self._render_source_edges(service_node, root_path),
        )
        return mermaid_syntax.MermaidDiagram(service_node=service_node, all_edges=all_edges).render_every_line()

    def _render_source_edges(
        self,
        service_node: diagram_model.DiagramNode,
        root_path: pathlib.Path,
        /,
    ) -> tuple[diagram_model.DiagramEdge, ...]:
        py_files: typing.Final = sorted(
            one_source_file
            for one_source_file in root_path.rglob(settings.FILES_SEARCH_PATTERN)
            if settings.SKIPPED_DIR_NAMES.isdisjoint(one_source_file.relative_to(root_path).parts)
        )
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            all_file_edges: typing.Final = executor.map(
                functools.partial(self._render_one_file_edges, service_node),
                py_files,
            )
            return tuple(one_edge for one_file_edges in all_file_edges for one_edge in one_file_edges)

    def _render_one_file_edges(
        self,
        service_node: diagram_model.DiagramNode,
        one_source_file: pathlib.Path,
        /,
    ) -> tuple[diagram_model.DiagramEdge, ...]:
        raw_file_source: typing.Final = _read_source_text(one_source_file)
        return tuple(
            one_edge
            for one_feature_functions in mapping.MAPPING_OF_PARSERS_AND_RENDERERS.values()
            for one_edge in one_feature_functions.render_edges(
                service_node,
                one_feature_functions.parse_source(raw_file_source),
            )
        )
