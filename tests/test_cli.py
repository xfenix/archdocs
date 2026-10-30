import io
import pathlib
import runpy
import sys
import types
import typing

import pytest

from archdocs import cli
from tests import diagram_rendering


_SERVICE_NAME: typing.Final = "cli-svc"
_CLI_ARGUMENTS: typing.Final = (
    "render",
    "--root-dir",
    str(diagram_rendering.LITESTAR_ROOT),
    "--service-name",
    _SERVICE_NAME,
    "--kubernetes-dir",
    diagram_rendering.WITHOUT_MANIFESTS,
)
_USAGE_EXIT_CODE: typing.Final = 2
_FORMAT_OPTION: typing.Final = "--format"
_SERVICE_NODE: typing.Final = 'cli_svc{"cli-svc"}'
_SELF_HOSTED_MERMAID: typing.Final = "/static/mermaid.min.js?v=1&x=2"
_ALL_FORMAT_CASES: typing.Final = types.MappingProxyType(
    {
        "mermaid by default": ((), "graph TB\n", "\n", ("```", "<html")),
        "markdown": ((_FORMAT_OPTION, "markdown"), "```mermaid\ngraph TB\n", "\n```\n", ("<html",)),
        "html with self hosted mermaid": (
            (_FORMAT_OPTION, "html", "--mermaid-script-url", _SELF_HOSTED_MERMAID),
            "<!DOCTYPE html>",
            "</html>",
            ("cdn.jsdelivr.net", _SELF_HOSTED_MERMAID),
        ),
    },
)


@pytest.mark.parametrize(
    ("extra_arguments", "expected_start", "expected_end", "forbidden_parts"),
    _ALL_FORMAT_CASES.values(),
    ids=_ALL_FORMAT_CASES,
)
def test_every_format_is_written_to_a_file(
    tmp_path: pathlib.Path,
    extra_arguments: tuple[str, ...],
    expected_start: str,
    expected_end: str,
    forbidden_parts: tuple[str, ...],
) -> None:
    output_path: typing.Final = tmp_path / "architecture.out"

    cli.run_command_line([*_CLI_ARGUMENTS, *extra_arguments, "--output", str(output_path)])

    rendered_output: typing.Final = output_path.read_text(encoding="utf-8")
    assert rendered_output.startswith(expected_start)
    assert rendered_output.endswith(expected_end)
    assert _SERVICE_NODE in rendered_output
    for one_forbidden_part in forbidden_parts:
        assert one_forbidden_part not in rendered_output, one_forbidden_part


def test_self_hosted_mermaid_is_escaped(tmp_path: pathlib.Path) -> None:
    output_path: typing.Final = tmp_path / "architecture.html"

    cli.run_command_line(
        [
            *_CLI_ARGUMENTS,
            _FORMAT_OPTION,
            "html",
            "--mermaid-script-url",
            _SELF_HOSTED_MERMAID,
            "--output",
            str(output_path),
        ],
    )

    assert '<script src="/static/mermaid.min.js?v=1&amp;x=2"></script>' in output_path.read_text(encoding="utf-8")


def test_module_run_prints_the_diagram(monkeypatch: pytest.MonkeyPatch) -> None:
    printed_output_buffer: typing.Final = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["archdocs", *_CLI_ARGUMENTS])
    monkeypatch.setattr(sys, "stdout", printed_output_buffer)

    runpy.run_module("archdocs", run_name="__main__")

    printed_output: typing.Final = printed_output_buffer.getvalue()
    assert printed_output.startswith("graph TB\n")
    assert _SERVICE_NODE in printed_output


@pytest.mark.parametrize(
    "every_argument",
    [(), ("render",), ("render", "--service-name", _SERVICE_NAME, _FORMAT_OPTION, "pdf")],
    ids=["no command", "no service name", "unknown format"],
)
def test_bad_arguments_exit_with_usage(every_argument: tuple[str, ...]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.run_command_line(list(every_argument))

    assert exit_info.value.code == _USAGE_EXIT_CODE
