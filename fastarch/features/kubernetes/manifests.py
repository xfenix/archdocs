import dataclasses
import typing


_COMMENT_PREFIX: typing.Final = "#"
_INLINE_COMMENT_PREFIX: typing.Final = " #"
_TEMPLATE_MARKER: typing.Final = "{{"
_LIST_ITEM_PREFIX: typing.Final = "-"
_LIST_ITEM_INDENT: typing.Final = 2
_QUOTE_CHARACTERS: typing.Final = "\"'"
_MEANINGLESS_VALUES: typing.Final = frozenset(("{}", "[]", "null", "~"))


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ManifestValue:
    value_path: tuple[str, ...]
    raw_value: str


type ManifestValues = tuple[ManifestValue, ...]
type ValuePath = tuple[str, ...]
type ParentKeys = list[tuple[int, str]]


def _remove_list_prefix(raw_indent: int, raw_content: str, /) -> tuple[int, str]:
    if not raw_content.startswith(_LIST_ITEM_PREFIX):
        return raw_indent, raw_content
    return raw_indent + _LIST_ITEM_INDENT, raw_content[len(_LIST_ITEM_PREFIX) :].strip()


def _make_one_value(
    line_indent: int,
    value_key: str,
    raw_value: str,
    parent_keys: ParentKeys,
    /,
) -> ManifestValue | None:
    if not raw_value:
        parent_keys.append((line_indent, value_key))
        return None
    if _TEMPLATE_MARKER in raw_value or raw_value in _MEANINGLESS_VALUES:
        return None
    return ManifestValue(
        value_path=(*(one_parent_key for _, one_parent_key in parent_keys), value_key),
        raw_value=raw_value,
    )


def _read_one_pair(raw_indent: int, raw_content: str, parent_keys: ParentKeys, /) -> ManifestValue | None:
    line_indent, line_content = _remove_list_prefix(raw_indent, raw_content)
    value_key, key_separator, raw_value = line_content.partition(":")
    if not key_separator:
        return None
    while parent_keys and parent_keys[-1][0] >= line_indent:
        parent_keys.pop()
    return _make_one_value(
        line_indent,
        value_key.strip(),
        raw_value.partition(_INLINE_COMMENT_PREFIX)[0].strip().strip(_QUOTE_CHARACTERS),
        parent_keys,
    )


def _read_one_line(raw_line: str, parent_keys: ParentKeys, /) -> ManifestValue | None:
    line_content: typing.Final = raw_line.strip()
    if not line_content or line_content.startswith((_COMMENT_PREFIX, _TEMPLATE_MARKER)):
        return None
    return _read_one_pair(len(raw_line) - len(raw_line.lstrip()), line_content, parent_keys)


def read_manifest_values(raw_source: str) -> ManifestValues:
    # Templated yaml is not yaml, so the nesting is restored from the indentation alone and every
    # `{{ ... }}` value is dropped: what a rendered chart would put there is nobody's guess here.
    parent_keys: typing.Final[ParentKeys] = []
    all_read_values: typing.Final = [
        _read_one_line(one_raw_line, parent_keys) for one_raw_line in raw_source.split("\n")
    ]
    return tuple(one_value for one_value in all_read_values if one_value is not None)
