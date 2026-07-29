import json
import pathlib
import typing


COVERAGE_REPORT_PATH: typing.Final = pathlib.Path("coverage.json")
BADGE_TARGET_PATH: typing.Final = pathlib.Path(".github/badges/coverage.json")
LOW_BOUNDARY: typing.Final = 60.0
HIGH_BOUNDARY: typing.Final = 80.0
POOR_COVERAGE_COLOR: typing.Final = "#E63946"
FAIR_COVERAGE_COLOR: typing.Final = "#FFB347"
GOOD_COVERAGE_COLOR: typing.Final = "#2A9D8F"


def choose_badge_color(coverage_percent: float) -> str:
    if coverage_percent < LOW_BOUNDARY:
        return POOR_COVERAGE_COLOR
    if coverage_percent < HIGH_BOUNDARY:
        return FAIR_COVERAGE_COLOR
    return GOOD_COVERAGE_COLOR


def read_coverage_display() -> str:
    return str(json.loads(COVERAGE_REPORT_PATH.read_text())["totals"]["percent_covered_display"])


def build_badge_file() -> None:
    coverage_display: typing.Final = read_coverage_display()
    BADGE_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_TARGET_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "label": "coverage",
                "message": f"{coverage_display}%",
                "color": choose_badge_color(float(coverage_display)),
            },
            indent=2,
        )
        + "\n",
    )


if __name__ == "__main__":
    build_badge_file()
