# Python3 Rules To Live By

## Basics
There will be a DESIGN.md file describing the project (a PRD "light").  Read it and understand it.

## Workflow and Planning
**CRITICAL: Always read the current state of the project before planning any changes**
- Before making any modifications, ALWAYS read and understand the current state of relevant files
- Use codebase search and file reading tools to gather context about existing code
- Review related files, dependencies, and project structure before implementing changes
- Understand the full context of what you're modifying, including:
  - Existing implementations and patterns
  - Dependencies and imports
  - Related modules and functions
  - Current architecture and design decisions
- Think deeply about the implications of changes:
  - Consider edge cases and potential side effects
  - Analyze how changes will interact with existing code
  - Evaluate alternative approaches before committing to a solution
  - Consider long-term maintainability and scalability
  - Think about backward compatibility if applicable
- Never make assumptions about the codebase - always verify by reading the actual code
- Plan changes thoroughly before implementation, considering the full impact

## Language and Version
- Use Python 3.8+ syntax and features
- Prefer type hints for function parameters and return types
- Use f-strings for string formatting
- Follow PEP 8 style guidelines
- **ALWAYS use `uv`** as the Python package manager and environment tool (see Package and Environment Management)

## Code Style
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter default)
- Use descriptive variable and function names
- Prefer snake_case for functions and variables
- Use PascalCase for class names
- Use UPPER_CASE for constants

## Imports
- Group imports: standard library, third-party, local imports
- Use absolute imports when possible
- Sort imports alphabetically within each group
- Use `from __future__ import annotations` for forward references

## Type Hints
- Always add type hints to function signatures
- Use `Optional[Type]` or `Type | None` for nullable types
- Use `List[Type]`, `Dict[KeyType, ValueType]` or `list[Type]`, `dict[KeyType, ValueType]` for collections
- Import types from `typing` module when needed

## Error Handling
- Use specific exception types, not bare `except:`
- Include meaningful error messages
- Use context managers (`with` statements) for resource management
- Consider using `try/except/else/finally` blocks appropriately

## Documentation
- Write docstrings for all public functions, classes, and modules
- Use Google-style or NumPy-style docstrings
- Include parameter descriptions, return types, and raise conditions
- Add inline comments for complex logic

## Testing
- Write unit tests for new functionality
- Use pytest as the testing framework
- Name test files with `test_` prefix
- Keep tests simple and focused

## Dependencies
- Use a `requirements.txt` or `pyproject.toml` for dependency management
- Pin version numbers for reproducibility
- Document why each dependency is needed

## Package and Environment Management
- **ALWAYS use `uv`** for Python package and virtual environment management (never `pip`, `pip3`, `virtualenv`, or `venv` directly)
- Create virtual environments with `uv venv`
- Install packages with `uv pip install` or `uv add`
- Sync dependencies with `uv pip sync requirements.txt` or `uv sync`

## Versioning
- **`pyproject.toml` is the single source of truth** for the project version — never duplicate it elsewhere as a hardcoded string
- At runtime, read the version via `importlib.metadata.version("package-name")` with a `"0.0.0-dev"` fallback:
  ```python
  from importlib.metadata import PackageNotFoundError, version as _pkg_version
  try:
      VERSION = _pkg_version("my-package")
  except PackageNotFoundError:
      VERSION = "0.0.0-dev"
  ```
- The Makefile MUST include version management targets:
  - `make version` — print current version from `pyproject.toml`
  - `make version-increment` — bump the patch number in `pyproject.toml` in-place using `sed`
  - `make push` — run `format`, `lint`, `test`, bump patch version, `git commit -m "release: vX.Y.Z.  $(gitsum)"`, `git push`, `git tag`, `git push --tags`
  - Always use `gitsum` in the commit message of the `push` target to embed a git summary

## Makefile Requirement
**MANDATORY: Every project MUST have a Makefile kept up to date at all times**
- Create a `Makefile` at the project root for all projects
- The Makefile MUST include at minimum these standard targets:
  - `make venv` — create the virtual environment using `uv venv`
  - `make install` — install dependencies via `uv pip install` or `uv sync`
  - `make build` — build the project (compile, package, etc. as applicable)
  - `make run` — run the application
  - `make test` — run the test suite via `pytest`
  - `make lint` — run linters (e.g. `ruff`, `flake8`)
  - `make format` — auto-format code (e.g. `black`, `ruff format`)
  - `make clean` — remove build artifacts, `__pycache__`, `.venv`, etc.
  - `make help` — print available targets with brief descriptions
- Keep the Makefile up to date as new scripts, tools, or workflows are added
- Use `.PHONY` declarations for all non-file targets
- Add new targets whenever a repeated workflow or utility command is introduced

## Code Quality
- Use list comprehensions and generator expressions when appropriate
- Prefer `pathlib.Path` over `os.path` for file operations
- Use `dataclasses` or `@dataclass` decorator for simple data containers
- Consider using `enum.Enum` for constants with limited values

## Performance
- Use generators for large datasets
- Avoid premature optimization
- Profile code before optimizing
- Use `__slots__` for classes with many instances if memory is a concern

## Security
- Never hardcode secrets or API keys
- Use environment variables or secure configuration files
- Validate and sanitize user inputs
- Use parameterized queries for database operations

## README.md
- README.md file must be kept up to date with the base design at all times.  

## Git and Version Control
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Use meaningful branch names
- **MANDATORY**: Update `CHANGELOG.md` before every commit/checkin
- Never commit changes without updating `CHANGELOG.md` first

## CHANGELOG.md Documentation Requirement
**CRITICAL: CHANGELOG.md must ALWAYS be updated before checkin and for ALL changes**
- The `CHANGELOG.md` file MUST be updated for EVERY change made to the codebase, whether by humans or AI agents
- Update `CHANGELOG.md` BEFORE committing changes or creating pull requests
- Document all changes including:
  - New features and functionality
  - Bug fixes and patches
  - Configuration changes
  - Dependency updates
  - Documentation updates
  - Refactoring and code improvements
  - Breaking changes
- Use clear, descriptive entries that explain what changed and why
- Group changes by date or version as appropriate
- This is a mandatory step that must not be skipped

## README Documentation Requirement
**CRITICAL: All changes must be documented in README.md**
- After making any significant changes to the codebase, update the README.md file
- Document new features, bug fixes, configuration changes, and dependency updates
- Include a "Changelog" or "Updates" section in the README.md
- Update installation instructions if dependencies change
- Update usage examples if functionality changes
- Keep the README.md current and comprehensive

## Project-Specific Guidelines
- This is a hackathon project: prioritize working solutions over perfect code
- However, maintain code quality and readability
- Document architectural decisions in the README.md
- Keep the codebase organized and maintainable
