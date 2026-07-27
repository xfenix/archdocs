import itertools
import pathlib
import typing

from fastarch.features.helm import const


def _find_chart_dir_near_parents(root_path: pathlib.Path) -> pathlib.Path | None:
    for one_parent_path in list(root_path.parents)[: const.PARENT_LOOKUP_DEPTH]:
        for one_search_dir in const.CHART_SEARCH_DIRS:
            candidate_chart_files = sorted(
                itertools.chain.from_iterable(
                    (one_parent_path / one_search_dir).glob(one_chart_pattern)
                    for one_chart_pattern in const.PARENT_LOOKUP_PATTERNS
                ),
            )
            if candidate_chart_files:
                return candidate_chart_files[0].parent
    return None


def _find_chart_dir(root_path: pathlib.Path, configured_chart_dir: str | pathlib.Path | None, /) -> pathlib.Path | None:
    if configured_chart_dir is not None:
        explicit_chart_dir: typing.Final = pathlib.Path(configured_chart_dir).resolve()
        return explicit_chart_dir if explicit_chart_dir.is_dir() else None
    for one_nested_pattern in const.NESTED_LOOKUP_PATTERNS:
        nested_chart_files = sorted(root_path.glob(one_nested_pattern))
        if nested_chart_files:
            return nested_chart_files[0].parent
    return _find_chart_dir_near_parents(root_path)


def read_helm_chart_source(root_path: pathlib.Path, configured_chart_dir: str | pathlib.Path | None, /) -> str:
    chart_dir: typing.Final = _find_chart_dir(root_path, configured_chart_dir)
    if chart_dir is None:
        return ""
    all_manifest_files: typing.Final[list[pathlib.Path]] = []
    for one_search_pattern in const.MANIFEST_SEARCH_PATTERNS:
        all_manifest_files.extend(sorted(chart_dir.glob(one_search_pattern)))
    return "".join(f"{one_manifest_file.read_text()}\n" for one_manifest_file in all_manifest_files)
