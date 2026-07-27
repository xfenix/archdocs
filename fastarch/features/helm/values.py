import re as py_re
import typing

from fastarch.features.helm.const import ChartValueLine, ChartValueLines


TOP_LEVEL_BLOCK: typing.Final = ""
_TEMPLATE_MARKER: typing.Final = "{{"
_QUOTE_CHARACTERS: typing.Final = "\"'"
_LIST_ITEM_CHARACTERS: typing.Final = "- "
_TOP_LEVEL_BLOCK_PATTERN: typing.Final = py_re.compile(
    r"^(?P<block_name>[A-Za-z_][A-Za-z0-9_.-]*):[^\n]*\n(?P<block_body>(?:[ \t]+[^\n]*\n|[ \t]*\n)*)",
    flags=py_re.MULTILINE,
)
_TOP_LEVEL_SCALAR_PATTERN: typing.Final = py_re.compile(
    r"^(?P<value_key>[A-Za-z_][A-Za-z0-9_.-]*):[ \t]*(?P<raw_value>[^\n]*)$",
    flags=py_re.MULTILINE,
)


def _is_literal_value(one_value_line: ChartValueLine, block_name: str, value_key: str, /) -> bool:
    return (
        one_value_line.block_name == block_name
        and one_value_line.value_key == value_key
        and bool(one_value_line.raw_value)
        and _TEMPLATE_MARKER not in one_value_line.raw_value
    )


def _read_one_line(line_content: str, block_name: str, /) -> ChartValueLine | None:
    one_value_key, key_separator, one_raw_value = line_content.partition(":")
    if not key_separator:
        return None
    return ChartValueLine(
        block_name=block_name,
        value_key=one_value_key.strip(),
        raw_value=one_raw_value.strip().strip(_QUOTE_CHARACTERS),
    )


def _read_block_lines(block_body: str, block_name: str, /) -> list[ChartValueLine]:
    all_parsed_lines: typing.Final = [
        _read_one_line(one_body_line.strip().lstrip(_LIST_ITEM_CHARACTERS), block_name)
        for one_body_line in block_body.splitlines()
    ]
    return [one_value_line for one_value_line in all_parsed_lines if one_value_line is not None]


def read_chart_values(raw_source: str) -> ChartValueLines:
    return (
        *[
            one_value_line
            for one_block_match in _TOP_LEVEL_BLOCK_PATTERN.finditer(raw_source)
            for one_value_line in _read_block_lines(
                one_block_match.group("block_body"),
                one_block_match.group("block_name"),
            )
        ],
        *[
            ChartValueLine(
                block_name=TOP_LEVEL_BLOCK,
                value_key=one_scalar_match.group("value_key"),
                raw_value=one_scalar_match.group("raw_value").strip().strip(_QUOTE_CHARACTERS),
            )
            for one_scalar_match in _TOP_LEVEL_SCALAR_PATTERN.finditer(raw_source)
        ],
    )


def read_values(all_value_lines: ChartValueLines, block_name: str, value_key: str, /) -> tuple[str, ...]:
    all_matching_values: typing.Final = [
        one_value_line.raw_value
        for one_value_line in all_value_lines
        if _is_literal_value(one_value_line, block_name, value_key)
    ]
    return tuple(dict.fromkeys(all_matching_values))


def read_first_value(all_value_lines: ChartValueLines, block_name: str, value_key: str, /) -> str:
    all_literal_values: typing.Final = read_values(all_value_lines, block_name, value_key)
    return all_literal_values[0] if all_literal_values else ""


def read_int_value(all_value_lines: ChartValueLines, block_name: str, value_key: str, /) -> int:
    raw_value: typing.Final = read_first_value(all_value_lines, block_name, value_key)
    return int(raw_value) if raw_value.isdigit() else 0
