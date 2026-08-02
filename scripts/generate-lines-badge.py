import json
import pathlib
import typing


PACKAGE_PATH: typing.Final = pathlib.Path("archdocs")
BADGE_TARGET_PATH: typing.Final = pathlib.Path(".github/badges/lines.json")
THOUSAND: typing.Final = 1000
BADGE_COLOR: typing.Final = "#457B9D"


def count_code_lines(source_path: pathlib.Path) -> int:
    """Считает строки кода: пустые и строки-комментарии не в счёт, докстринги — в счёт."""
    return sum(
        1
        for one_line in source_path.read_text(encoding="utf-8").splitlines()
        if one_line.strip() and not one_line.lstrip().startswith("#")
    )


def count_package_lines() -> int:
    return sum(count_code_lines(one_module) for one_module in PACKAGE_PATH.rglob("*.py"))


def format_lines_display(lines_count: int) -> str:
    if lines_count < THOUSAND:
        return str(lines_count)
    return f"{lines_count / THOUSAND:.1f}k"


def build_badge_file() -> None:
    lines_count: typing.Final = count_package_lines()
    BADGE_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_TARGET_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "label": "lines of code",
                "message": format_lines_display(lines_count),
                "color": BADGE_COLOR,
            },
            indent=2,
        )
        + "\n",
    )


if __name__ == "__main__":
    build_badge_file()
