"""Check that more than just `.py` files land in the wheel.

`archdocs/template.html` is read when `settings.py` is imported. A wheel without the template
is not a "missing picture" — it is a `FileNotFoundError` on the very first `import archdocs.main`.
Neither tests nor linters see this: in the sources the file is in place, and the built wheel
never crosses their path. Building the wheel and looking inside is the only way to check.
"""

import pathlib
import shutil
import subprocess
import sys
import tempfile
import typing
import zipfile


PACKAGE_PATH: typing.Final = pathlib.Path("archdocs")
SOURCE_SUFFIX: typing.Final = ".py"
IGNORED_DIR_NAMES: typing.Final = frozenset(("__pycache__",))
WHEEL_PATTERN: typing.Final = "*.whl"


def collect_required_files() -> tuple[str, ...]:
    return tuple(
        sorted(
            one_package_file.as_posix()
            for one_package_file in PACKAGE_PATH.rglob("*")
            if one_package_file.is_file()
            and one_package_file.suffix != SOURCE_SUFFIX
            and IGNORED_DIR_NAMES.isdisjoint(one_package_file.parts)
        ),
    )


def build_wheel_into(build_dir: pathlib.Path, /) -> pathlib.Path:
    uv_executable: typing.Final = shutil.which("uv")
    if uv_executable is None:
        sys.exit("uv not found in PATH: nothing to build the wheel with")
    # The build output is hidden while the build succeeds and shown in full when it does not:
    # the check lives in `just lint`, where a traceback without the failure reason helps nobody.
    finished_build: typing.Final = subprocess.run(  # noqa: S603 — the command is fixed, no user input here
        [uv_executable, "build", "--wheel", "--out-dir", str(build_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    if finished_build.returncode:
        sys.exit(
            f"uv build exited with code {finished_build.returncode}:\n{finished_build.stdout}{finished_build.stderr}",
        )
    all_built_wheels: typing.Final = sorted(build_dir.glob(WHEEL_PATTERN))
    if not all_built_wheels:
        sys.exit(f"uv build finished successfully but left no wheel in {build_dir}")
    return all_built_wheels[0]


def find_missing_files() -> tuple[str, ...]:
    required_files: typing.Final = collect_required_files()
    with tempfile.TemporaryDirectory() as build_dir_name:
        built_wheel: typing.Final = build_wheel_into(pathlib.Path(build_dir_name))
        with zipfile.ZipFile(built_wheel) as opened_wheel:
            packed_names: typing.Final = frozenset(opened_wheel.namelist())
    return tuple(one_required_file for one_required_file in required_files if one_required_file not in packed_names)


def report_missing_files() -> None:
    missing_files: typing.Final = find_missing_files()
    if not missing_files:
        return
    sys.stdout.write(f"Package files missing from the wheel: {', '.join(missing_files)}\n")
    sys.exit(1)


if __name__ == "__main__":
    report_missing_files()
