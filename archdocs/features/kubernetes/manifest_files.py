import pathlib
import re as py_re
import typing

from archdocs import settings
from archdocs.features.kubernetes import const


_API_VERSION_PATTERN: typing.Final = py_re.compile(r"^apiVersion:", flags=settings.TYPICAL_RE_FLAGS)
_KIND_PATTERN: typing.Final = py_re.compile(r"^kind:", flags=settings.TYPICAL_RE_FLAGS)


def _is_manifest_file(one_file_path: pathlib.Path, /) -> bool:
    if one_file_path.stem == const.VALUES_FILE_STEM:
        return True
    file_source: typing.Final = one_file_path.read_text(errors="ignore")
    return bool(_API_VERSION_PATTERN.search(file_source) and _KIND_PATTERN.search(file_source))


def _find_manifest_files(search_dir: pathlib.Path, /) -> list[pathlib.Path]:
    all_found_files: typing.Final = (
        one_found_file
        for one_file_suffix in const.MANIFEST_FILE_SUFFIXES
        for one_found_file in search_dir.rglob(f"*{one_file_suffix}")
        if settings.SKIPPED_DIR_NAMES.isdisjoint(one_found_file.relative_to(search_dir).parts)
    )
    return sorted(
        (one_found_file for one_found_file in all_found_files if _is_manifest_file(one_found_file)),
        key=lambda one_found_file: (len(one_found_file.parts), one_found_file),
    )


def _iter_search_roots(root_path: pathlib.Path, /) -> typing.Iterator[pathlib.Path]:
    # Charts live next to the sources at least as often as inside them, so the search climbs a
    # couple of levels up — but never out of the repository the sources belong to.
    for one_search_root in (root_path, *list(root_path.parents)[: const.PARENT_SEARCH_DEPTH]):
        yield one_search_root
        if (one_search_root / const.REPOSITORY_MARKER_NAME).exists():
            return


def _find_manifest_dir(search_dir: pathlib.Path, /) -> pathlib.Path | None:
    all_manifest_files: typing.Final = _find_manifest_files(search_dir)
    if not all_manifest_files:
        return None
    closest_manifest_dir: typing.Final = all_manifest_files[0].parent
    if closest_manifest_dir.name == const.TEMPLATES_DIR_NAME:
        return closest_manifest_dir.parent
    return closest_manifest_dir


def _resolve_manifest_dir(root_path: pathlib.Path, configured_dir: str | pathlib.Path | None, /) -> pathlib.Path | None:
    if configured_dir is None:
        return next(
            (
                one_found_dir
                for one_found_dir in map(_find_manifest_dir, _iter_search_roots(root_path))
                if one_found_dir is not None
            ),
            None,
        )
    all_candidate_dirs: typing.Final = (
        (one_search_root / configured_dir).resolve() for one_search_root in _iter_search_roots(root_path)
    )
    return next((one_candidate_dir for one_candidate_dir in all_candidate_dirs if one_candidate_dir.is_dir()), None)


def read_kubernetes_manifests(root_path: pathlib.Path, configured_dir: str | pathlib.Path | None, /) -> str:
    manifest_dir: typing.Final = _resolve_manifest_dir(root_path, configured_dir)
    if manifest_dir is None:
        return ""
    return "".join(
        f"{one_manifest_file.read_text(errors='ignore')}\n" for one_manifest_file in _find_manifest_files(manifest_dir)
    )
