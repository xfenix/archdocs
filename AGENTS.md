# AGENTS.md - Руководство для AI-агентов

## Описание проекта

**fastarch** — это инструмент для автоматической генерации архитектурных схем из кода Python. Он анализирует структуру приложения, включая базы данных, очереди сообщений, кэширование и HTTP-эндпоинты, и создает визуализацию архитектуры.

### Ключевые принципы

- **Code-first подход**: Не требует модификации существующего кода
- **Автоматическое обнаружение**: Библиотека автоматически ищет все необходимые компоненты
- **Визуализация**: Использует Mermaid.js для создания интерактивных диаграмм
- **Модульность**: Легко расширяется новыми фичами

## Архитектура проекта

### Структура модулей

```
fastarch/
├── features/           # Модули для различных технологий
│   ├── http_api/      # FastAPI/Litestar endpoints
│   ├── http_clients/  # HTTP clients (httpx, aiohttp, requests, niquests)
│   ├── sqlalchemy/    # Database ORM
│   ├── redis/         # Caching layer
│   ├── messaging_queue/ # Message queues (FastStream)
│   └── task_queues/   # Task queues (Celery, Taskiq, Arq, RQ, Dramatiq, Huey)
├── integrations/      # Интеграции с веб-фреймворками
├── main.py           # Основной движок
├── mapping.py        # Регистрация парсеров/рендереров
└── settings.py       # Конфигурация
```

### Паттерн Parser/Renderer

Каждая фича следует единому паттерну:

1. **`const.py`** - Data-классы для хранения найденных фич
2. **`parser.py`** - Regex-парсинг исходного кода
3. **`renderer.py`** - Генерация Mermaid диаграмм

### Система маппинга

```python
MAPPING_OF_PARSERS_AND_RENDERERS = {
    AllCurrentFeatures.FASTAPI_LITESTAR: _FeatureFunctions(
        parse=httpapi_parser.find_fastapi_and_litestar_features,
        render=httpapi_renderer.draw_http_api_features,
    ),
    # ... другие фичи
}
```

## Стиль кодирования

### Основные принципы

Проект следует строгим правилам кодирования, основанным на [pylines code-style](https://github.com/community-of-python/pylines/blob/main/code-style.md):

#### 1. Type Hints и Immutability

```python
# Всегда используйте typing.Final для констант
_TARGET_SESSION_ATTRS_PATTERN: typing.Final = py_re.compile(
    r"target_session_attrs\s*=\s*['\"](\w+)['\"]",
    flags=settings.TYPICAL_RE_FLAGS,
)

# Data-классы должны быть frozen и использовать slots
@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HTTPApiFeatures:
    in_methods: frozenset[str]
    out_methods: frozenset[str]
    in_methods_existed: bool
    out_methods_existed: bool
```

#### 2. Импорты и именование

```python
# Избегайте конфликтов имен
import re as py_re
import types
import typing

# Используйте MappingProxyType для immutable mappings
_REDIS_CONNECTION_PATTERNS: typing.Final = types.MappingProxyType({
    "plain": py_re.compile(r"\b(?:redis\.|from\s+redis\s+import\s+).*\bRedis\b"),
    "sentinel": py_re.compile(r"\b(?:redis\.sentinel\.|from\s+redis(?:\.sentinel)?\s+import\s+).*\bSentinel\b"),
})
```

#### 3. Функции парсеров

```python
def find_sqlalchemy_features(raw_source: str) -> SQLAlchemyFeatures:
    # Early return при отсутствии нужных паттернов
    if not _ASYNC_ENGINE_PATTERN.search(raw_source):
        return SQLAlchemyFeatures(
            async_used=False,
            pooling_used=False,
            multiple_hosts=False,
            target_session_attrs="",
            database_type="",
        )

    # Обработка найденных паттернов
    _target_session_attrs_match: typing.Final = _TARGET_SESSION_ATTRS_PATTERN.search(raw_source)
    return SQLAlchemyFeatures(
        target_session_attrs=_target_session_attrs_match.group(1) if _target_session_attrs_match else "",
        # ... другие поля
    )
```

#### 4. Функции рендереров

```python
def draw_http_api_features(service_name: str, features_to_draw: HTTPApiFeatures) -> str:
    # Early return при отсутствии фич
    if not features_to_draw.in_methods_existed and not features_to_draw.out_methods_existed:
        return ""

    diagram_parts: typing.Final[list[str]] = []
    if features_to_draw.in_methods_existed:
        diagram_parts.append(
            f"{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA} --> "
            f"|REST ({', '.join(features_to_draw.in_methods)});| {{{service_name}}}",
        )
    return "\n".join(diagram_parts)
```

### Конфигурация инструментов

#### Ruff (pyproject.toml)

```toml
[tool.ruff]
line-length = 120
select = ["ALL"]
ignore = ["EM", "FBT", "TRY003", "D1", "D203", "D213", "G004", "FA", "COM812", "ISC001"]

[tool.ruff.format]
quote-style = "preserve"  # Сохранять оригинальные кавычки
```

#### Justfile

```justfile
lint:
    uv run ruff format
    uv run ruff check --fix
    uv run mypy .
    uv run flake8 --select=WPS --extend-exclude=tests/fastapi fastarch tests
```

## Как добавить новую фичу

### Шаг 1: Создание структуры

```bash
mkdir fastarch/features/new_technology
touch fastarch/features/new_technology/__init__.py
touch fastarch/features/new_technology/const.py
touch fastarch/features/new_technology/parser.py
touch fastarch/features/new_technology/renderer.py
```

### Шаг 2: Реализация const.py

```python
import dataclasses
import typing

@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class NewTechnologyFeatures:
    feature_detected: bool
    specific_property: str = ""
    another_property: int = 0
```

### Шаг 3: Реализация parser.py

```python
import re as py_re
import typing

from fastarch import settings
from fastarch.features.new_technology.const import NewTechnologyFeatures

_TECHNOLOGY_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+new_tech\b|import\s+new_tech\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)

def find_new_technology_features(raw_source: str) -> NewTechnologyFeatures:
    if not _TECHNOLOGY_IMPORT_PATTERN.search(raw_source):
        return NewTechnologyFeatures(feature_detected=False)

    # Анализ специфичных паттернов
    return NewTechnologyFeatures(
        feature_detected=True,
        specific_property="detected_value",
    )
```

### Шаг 4: Реализация renderer.py

```python
import typing

from fastarch import settings
from fastarch.features.new_technology.const import NewTechnologyFeatures

def draw_new_technology_features(service_name: str, features_to_draw: NewTechnologyFeatures) -> str:
    if not features_to_draw.feature_detected:
        return ""

    return f"{settings.SHIFT_LEFT}{{{service_name}}} --> |{features_to_draw.specific_property}| new_tech_service"
```

### Шаг 5: Регистрация в mapping.py

```python
# В AllCurrentFeatures enum
class AllCurrentFeatures(enum.Enum):
    # ... существующие
    NEW_TECHNOLOGY = 5

# В MAPPING_OF_PARSERS_AND_RENDERERS
MAPPING_OF_PARSERS_AND_RENDERERS = types.MappingProxyType({
    # ... существующие
    AllCurrentFeatures.NEW_TECHNOLOGY: _FeatureFunctions(
        parse=new_technology_parser.find_new_technology_features,
        render=new_technology_renderer.draw_new_technology_features,
    ),
})
```

## Тестирование

### Unit-тесты для парсеров

```python
from hypothesis import given, strategies as st
from fastarch.features.http_api.parser import find_fastapi_and_litestar_features

@given(st.sampled_from(["post", "put", "patch", "delete"]))
def test_find_fastapi_and_litestar_features_detects_methods(method: str) -> None:
    src = (
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        f"@router.{method}('/x')\n"
        "async def endpoint() -> None:\n"
        "    pass\n"
    )
    features = find_fastapi_and_litestar_features(src)
    assert method in features.in_methods
    assert features.in_methods_existed
```

### Интеграционные тесты

```python
def test_add_architecture_doc_routes(fastapi_app: FastAPI) -> None:
    _root_for_fastapi_example_src: typing.Final = pathlib.Path(__file__).parent / "fastapi"
    add_architecture_doc_routes(
        fastapi_app,
        arch_settings=SettingsForFastarch(root_dir=_root_for_fastapi_example_src, service_name="test"),
    )
    client_for_test: typing.Final = TestClient(fastapi_app)
    assert client_for_test.get(settings.DEFAULT_PATH).status_code == 200
```

## Важные замечания для AI-агентов

### 1. Immutability First

- Всегда используйте `frozen=True` для dataclasses
- Предпочитайте `frozenset` вместо `set`
- Используйте `types.MappingProxyType` для immutable mappings

### 2. Type Safety

- Всегда аннотируйте типы с `typing.Final`
- Используйте `@typing.final` для классов, которые не должны наследоваться
- Предпочитайте `kw_only=True` для dataclasses

### 3. Performance

- Используйте `slots=True` для dataclasses
- Применяйте `ThreadPoolExecutor` для обработки множества файлов
- Кэшируйте результаты парсинга

### 4. Regex Patterns

- Всегда используйте `settings.TYPICAL_RE_FLAGS`
- Компилируйте паттерны как `typing.Final`
- Избегайте конфликтов имен с `import re as py_re`

### 5. Mermaid Generation

- Генерируйте валидный Mermaid синтаксис
- Используйте `settings.SHIFT_LEFT` для отступов
- Проверяйте диаграммы в Mermaid Live Editor

### 6. Testing Strategy

- Используйте Hypothesis для property-based тестирования
- Тестируйте edge cases (пустые строки, отсутствие паттернов)
- Покрывайте все ветки кода

## Инструменты разработки

### Основные команды

```bash
# Установка зависимостей
just install

# Линтинг и форматирование
just lint

# Запуск тестов
just test

# Публикация пакета
just publish
```

### Зависимости

- **uv**: Управление зависимостями и виртуальными окружениями
- **Ruff**: Линтинг и форматирование кода
- **mypy**: Статическая проверка типов
- **pytest**: Фреймворк для тестирования
- **hypothesis**: Property-based тестирование
- **wemake-python-styleguide**: Дополнительные правила линтинга

## Примеры использования

### FastAPI интеграция

```python
from fastapi import FastAPI
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch

app = FastAPI()

# Добавление маршрута архитектурной документации
add_architecture_doc_routes(
    app,
    arch_settings=SettingsForFastarch(
        root_dir="src/",
        service_name="my-service"
    )
)
```

### Кастомные настройки

```python
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch

# Создание кастомного движка
engine = ArchitectureParserAndRenderer(
    SettingsForFastarch(
        root_dir="/path/to/project",
        service_name="custom-service"
    )
)

# Генерация диаграммы
mermaid_diagram = engine.search_features_and_draw_them()
```

## Roadmap и TODO

### Краткосрочные цели

- [ ] Завершить README с примерами и скриншотами
- [ ] Исправить dependencies в pyproject.toml
- [ ] Добавить больше тестов для парсеров

### Среднесрочные цели

- [ ] Реализовать парсинг Helm charts и docker-compose
- [ ] AST-based парсинг вместо/вместе с regex
- [ ] Поддержка других фреймворков (Django, Flask, Sanic)

### Долгосрочные цели

- [ ] Интерактивная схема с zoom и фильтрами
- [ ] Анализ потоков данных и зависимостей
- [ ] Интеграция с системами мониторинга

---

Этот документ служит полным руководством для AI-агентов при работе с проектом fastarch. Следуйте указанным принципам и паттернам для обеспечения консистентности и качества кода.
