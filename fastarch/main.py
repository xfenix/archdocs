import dataclasses
import itertools
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


def _find_helm_chart_near_parents(root_path: pathlib.Path) -> pathlib.Path | None:
    # Charts usually live next to the sources rather than inside them, a `root_dir` of
    # `src/` with a chart in `deploy/` is the common layout. The lookup stays on the two
    # conventional depths instead of recursing, so an unrelated huge sibling tree above
    # the sources can never turn discovery into a full disk walk.
    for one_parent_path in list(root_path.parents)[: settings.HELM_PARENT_LOOKUP_DEPTH]:
        for one_search_dir in settings.HELM_CHART_SEARCH_DIRS:
            candidate_chart_files = sorted(
                itertools.chain.from_iterable(
                    (one_parent_path / one_search_dir).glob(one_chart_pattern)
                    for one_chart_pattern in settings.HELM_CHART_LOOKUP_PATTERNS
                ),
            )
            if candidate_chart_files:
                return candidate_chart_files[0].parent
    return None


def _find_helm_chart_dir(
    root_path: pathlib.Path,
    configured_chart_dir: str | pathlib.Path | None,
) -> pathlib.Path | None:
    if configured_chart_dir is not None:
        explicit_chart_dir: typing.Final = pathlib.Path(configured_chart_dir).resolve()
        return explicit_chart_dir if explicit_chart_dir.is_dir() else None
    # Depth by depth instead of one rglob: this returns the shallowest chart, stays
    # deterministic through the per depth sort, and stops as soon as it finds one
    # rather than collecting every match in the tree first.
    for one_nested_pattern in settings.HELM_NESTED_LOOKUP_PATTERNS:
        nested_chart_files = sorted(root_path.glob(one_nested_pattern))
        if nested_chart_files:
            return nested_chart_files[0].parent
    return _find_helm_chart_near_parents(root_path)


def _read_helm_chart_source(chart_dir: pathlib.Path) -> str:
    all_manifest_files: typing.Final[list[pathlib.Path]] = []
    for one_search_pattern in settings.HELM_MANIFEST_SEARCH_PATTERNS:
        all_manifest_files.extend(sorted(chart_dir.glob(one_search_pattern)))
    # Every manifest keeps its own trailing newline, the block patterns expect
    # each YAML line to be terminated.
    return "".join(f"{one_manifest_file.read_text()}\n" for one_manifest_file in all_manifest_files)


def _render_manifest_features(raw_manifest_source: str) -> tuple[tuple[str, ...], str]:
    all_parsed_manifests: typing.Final = [
        (one_manifest_functions, one_manifest_functions.parse_manifests(raw_manifest_source))
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
        node_annotations, manifest_diagram = self._process_manifest_sources(root_path)
        all_diagram_lines: typing.Final = [
            mermaid_syntax.render_service_node_definition(self.local_settings.service_name, node_annotations),
            *manifest_diagram.split("\n"),
            *self._process_source_files(root_path).split("\n"),
        ]
        # Every source file re-renders the same edges, dict.fromkeys drops the repeats in place.
        full_result: typing.Final = "\n".join(dict.fromkeys(filter(None, all_diagram_lines)))
        self._cache.append(full_result)
        return full_result

    def _process_manifest_sources(self, root_path: pathlib.Path) -> tuple[tuple[str, ...], str]:
        chart_dir: typing.Final = _find_helm_chart_dir(root_path, self.local_settings.helm_chart_dir)
        if chart_dir is None:
            return (), ""
        return _render_manifest_features(_read_helm_chart_source(chart_dir))

    def _process_source_files(self, root_path: pathlib.Path) -> str:
        # rglob order depends on the filesystem while executor.map preserves the input
        # order, so sorting the input is what makes the whole diagram deterministic.
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
