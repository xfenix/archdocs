import itertools
import pathlib
import typing

from fastarch.features.helm import const


def _has_project_root_marker(checked_dir_path: pathlib.Path, /) -> bool:
    return any((checked_dir_path / one_marker_name).exists() for one_marker_name in const.PROJECT_ROOT_MARKERS)


def _iter_lookup_dirs(root_path: pathlib.Path, /) -> typing.Iterator[pathlib.Path]:
    yield root_path
    if _has_project_root_marker(root_path):
        return
    for one_parent_path in list(root_path.parents)[: const.PARENT_LOOKUP_DEPTH]:
        if one_parent_path == one_parent_path.parent:
            return
        yield one_parent_path
        if _has_project_root_marker(one_parent_path):
            return


def _find_first_chart_dir(search_path: pathlib.Path, search_patterns: tuple[str, ...], /) -> pathlib.Path | None:
    candidate_chart_files: typing.Final = sorted(
        itertools.chain.from_iterable(search_path.glob(one_chart_pattern) for one_chart_pattern in search_patterns),
    )
    return candidate_chart_files[0].parent if candidate_chart_files else None


def _find_chart_dir_by_lookup(root_path: pathlib.Path, /) -> pathlib.Path | None:
    nested_chart_dir: typing.Final = _find_first_chart_dir(root_path, const.NESTED_LOOKUP_PATTERNS)
    if nested_chart_dir is not None:
        return nested_chart_dir
    all_parent_chart_dirs: typing.Final = (
        _find_first_chart_dir(one_lookup_dir / one_search_dir, const.PARENT_LOOKUP_PATTERNS)
        for one_lookup_dir, one_search_dir in itertools.product(
            tuple(_iter_lookup_dirs(root_path))[1:],
            const.CHART_SEARCH_DIRS,
        )
    )
    return next((one_chart_dir for one_chart_dir in all_parent_chart_dirs if one_chart_dir is not None), None)


def _resolve_configured_chart_dir(
    root_path: pathlib.Path,
    configured_chart_dir: str | pathlib.Path,
    /,
) -> pathlib.Path | None:
    configured_path: typing.Final = pathlib.Path(configured_chart_dir)
    if configured_path.is_absolute():
        return configured_path if configured_path.is_dir() else None
    all_candidate_chart_dirs: typing.Final = (
        (one_lookup_dir / configured_path).resolve() for one_lookup_dir in _iter_lookup_dirs(root_path)
    )
    return next((one_chart_dir for one_chart_dir in all_candidate_chart_dirs if one_chart_dir.is_dir()), None)


def _find_chart_dir(root_path: pathlib.Path, configured_chart_dir: str | pathlib.Path | None, /) -> pathlib.Path | None:
    if configured_chart_dir is not None:
        return _resolve_configured_chart_dir(root_path, configured_chart_dir)
    return _find_chart_dir_by_lookup(root_path)


def read_helm_chart_source(root_path: pathlib.Path, configured_chart_dir: str | pathlib.Path | None, /) -> str:
    chart_dir: typing.Final = _find_chart_dir(root_path, configured_chart_dir)
    if chart_dir is None:
        return ""
    all_manifest_files: typing.Final[list[pathlib.Path]] = []
    for one_search_pattern in const.MANIFEST_SEARCH_PATTERNS:
        all_manifest_files.extend(sorted(chart_dir.glob(one_search_pattern)))
    return "".join(f"{one_manifest_file.read_text()}\n" for one_manifest_file in all_manifest_files)
