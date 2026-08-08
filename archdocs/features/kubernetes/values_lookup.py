import typing

from archdocs.features.kubernetes import const


def _is_path_suffix(one_value: const.ManifestValue, value_path: const.ValuePath, /) -> bool:
    return one_value.value_path[-len(value_path) :] == value_path


def _contains_path(one_value: const.ManifestValue, value_path: const.ValuePath, /) -> bool:
    return any(
        one_value.value_path[one_offset : one_offset + len(value_path)] == value_path
        for one_offset in range(len(one_value.value_path))
    )


def read_values(all_values: const.ManifestValues, /, *all_value_paths: const.ValuePath) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            one_value.raw_value
            for one_value in all_values
            if any(_is_path_suffix(one_value, one_value_path) for one_value_path in all_value_paths)
        ),
    )


def read_first_value(all_values: const.ManifestValues, /, *all_value_paths: const.ValuePath) -> str:
    all_matched_values: typing.Final = read_values(all_values, *all_value_paths)
    return all_matched_values[0] if all_matched_values else ""


def read_int_value(all_values: const.ManifestValues, /, *all_value_paths: const.ValuePath) -> int:
    raw_value: typing.Final = read_first_value(all_values, *all_value_paths)
    return int(raw_value) if raw_value.isdigit() else 0


def has_any_block(all_values: const.ManifestValues, /, *all_value_paths: const.ValuePath) -> bool:
    return any(
        _contains_path(one_value, one_value_path) for one_value in all_values for one_value_path in all_value_paths
    )
