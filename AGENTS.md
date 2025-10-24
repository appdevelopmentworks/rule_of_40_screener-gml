# Agent Guidelines for Rule of 40 Screener

## Build/Lint/Test Commands
- **Install dev dependencies**: `pip install -e .[dev]`
- **Run all tests**: `pytest tests/`
- **Run single test**: `pytest tests/unit/test_rule40.py::test_function_name`
- **Run with coverage**: `pytest --cov=src --cov-report=html`
- **Format code**: `black .`
- **Lint code**: `ruff check .`
- **Type check**: `mypy src/`

## Code Style Guidelines
- **Python version**: 3.9+ with strict type hints required
- **Line length**: 88 characters (Black formatting)
- **Import style**: Use `ruff` for isort-compliant imports
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use custom exceptions from `core.domain.models`, log errors appropriately
- **Documentation**: Japanese comments preferred, docstrings in Japanese
- **Testing**: Use pytest with fixtures in `conftest.py`, mark tests with `@pytest.mark.unit/integration/ui/slow`
- **Architecture**: Follow clean architecture - adapters/data/domain/application layers
- **UI**: PySide6 + QFluentWidgets, separate UI logic from business logic
- **Config**: YAML-based configuration via `ConfigManager` in `core.data.config_loader`