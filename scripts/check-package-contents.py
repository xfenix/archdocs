"""Проверка, что в колесо попадает не только `.py`.

`archdocs/template.html` читается на импорте `settings.py`. Колесо без шаблона — это не
«потерялась картинка», это `FileNotFoundError` на первом же `import archdocs.main`.
Ни тесты, ни линтеры такого не видят: в исходниках файл лежит на месте, собранного колеса
они не касаются. Собрать колесо и посмотреть внутрь — единственный способ проверить.
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
        message: typing.Final = "uv not found on PATH, cannot build the wheel"
        raise RuntimeError(message)
    subprocess.run(  # noqa: S603 — команда сборки фиксирована, пользовательского ввода тут нет
        [uv_executable, "build", "--wheel", "--out-dir", str(build_dir)],
        check=True,
        capture_output=True,
    )
    return next(build_dir.glob(WHEEL_PATTERN))


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
    sys.stdout.write(f"Файлы пакета не попали в колесо: {', '.join(missing_files)}\n")
    sys.exit(1)


if __name__ == "__main__":
    report_missing_files()
