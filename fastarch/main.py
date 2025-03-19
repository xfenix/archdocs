import dataclasses
import pathlib
import typing
from concurrent import futures

from fastarch import settings
from fastarch.mapping import MAPPING_OF_PARSERS_AND_RENDERERS


"""TODO:

parsers from settings.py typical configuration
parsers from helm chart/manifests vital k8s information
parsers from docker-compose.yml?
"""


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class FeaturesInSourceFinder:
    root_dir: str | pathlib.Path
    service_name: str

    def _process_one_file(self, one_src_file: pathlib.Path) -> str:
        raw_file_source: typing.Final = one_src_file.read_text()
        return "".join(
            features_functions.render(self.service_name, features_functions.parse(raw_file_source))
            for features_functions in MAPPING_OF_PARSERS_AND_RENDERERS.values()
        ).strip()

    def search_features_and_draw_them(self) -> str:
        py_files: typing.Final = list(pathlib.Path(self.root_dir).rglob(settings.FILES_SEARCH_PATTERN))
        buffer_of_results: list[str] = []
        with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            buffer_of_results = executor.map(self._process_one_file, py_files)
        return "\n".join(filter(None, buffer_of_results))
