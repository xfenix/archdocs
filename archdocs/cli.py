import argparse
import enum
import pathlib
import sys
import types
import typing

from archdocs import page, settings
from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs


@typing.final
class OutputFormat(enum.StrEnum):
    mermaid_text = "mermaid"
    markdown_text = "markdown"
    html_page = "html"


_RENDERERS_OF_FORMAT: typing.Final = types.MappingProxyType(
    {
        OutputFormat.mermaid_text: page.render_mermaid_text,
        OutputFormat.markdown_text: page.render_markdown_text,
        OutputFormat.html_page: page.render_architecture_page,
    },
)


def _build_argument_parser() -> argparse.ArgumentParser:
    root_parser: typing.Final = argparse.ArgumentParser(prog="archdocs")
    render_parser: typing.Final = root_parser.add_subparsers(dest="command_name", required=True).add_parser(
        "render", help="render the architecture diagram"
    )
    render_parser.add_argument("--root-dir", default=".", help="where the sources of the service live")
    render_parser.add_argument("--service-name", required=True, help="label of the service on the diagram")
    render_parser.add_argument("--kubernetes-dir", default=None, help="manifests or helm chart, from root-dir")
    render_parser.add_argument(
        "--format",
        dest="output_format",
        type=OutputFormat,
        choices=tuple(OutputFormat),
        default=OutputFormat.mermaid_text,
    )
    render_parser.add_argument("--output", type=pathlib.Path, default=None, help="file to write, stdout if omitted")
    render_parser.add_argument("--mermaid-script-url", default=settings.DEFAULT_MERMAID_SCRIPT_URL)
    return root_parser


def run_command_line(every_argument: typing.Sequence[str] | None = None) -> None:
    parsed_arguments: typing.Final = _build_argument_parser().parse_args(every_argument)
    arch_engine: typing.Final = ArchitectureParserAndRenderer(
        local_settings=SettingsForArchdocs(
            root_dir=parsed_arguments.root_dir,
            service_name=parsed_arguments.service_name,
            kubernetes_dir=parsed_arguments.kubernetes_dir,
            mermaid_script_url=parsed_arguments.mermaid_script_url,
        ),
    )
    rendered_output: typing.Final = _RENDERERS_OF_FORMAT[parsed_arguments.output_format](arch_engine)
    if parsed_arguments.output is None:
        sys.stdout.write(rendered_output)
        return
    parsed_arguments.output.write_text(rendered_output, encoding="utf-8")
