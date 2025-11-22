# Contributing to MentoDB

Thank you for your interest in contributing to MentoDB! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🧪 Add tests
- 🎨 Improve code quality

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/MentoDB.git
cd MentoDB
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 💻 Development Workflow

### Code Style

We use modern Python tooling to maintain code quality:

```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .
ruff check --fix .  # Auto-fix issues

# Type checking with MyPy
mypy .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mentodb --cov-report=html

# Run specific test file
pytest tests/test_connection.py

# Run specific test
pytest tests/test_mento.py::TestMento::test_insert_and_select
```

### Writing Tests

All new features must include tests:

```python
# tests/test_feature.py
import pytest
from mentodb import Mento, MentoConnection

class TestYourFeature:
    def test_your_feature(self):
        """Test description."""
        with MentoConnection(":memory:") as conn:
            db = Mento(conn)
            # Test code here
            assert result == expected
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style (Black + Ruff)
- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Type hints are added
- [ ] Commit messages are clear

### Commit Message Format

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat(insert): add batch insert support"
git commit -m "fix(select): handle empty result sets correctly"
git commit -m "docs(readme): update installation instructions"
```

### Pull Request Process

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your changes:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request:**
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Link related issues

4. **Code Review:**
   - Address review comments
   - Push updates to your branch
   - Request re-review

5. **Merge:**
   - Once approved, a maintainer will merge your PR

## 🐛 Bug Reports

### Before Reporting

- Search existing issues
- Verify bug on latest version
- Collect reproduction steps

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. ...
2. ...
3. ...

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12.0]
- MentoDB version: [e.g., 2.0.0]

**Additional context**
Any other relevant information.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Clear description of what you want.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## 🔒 Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email: [Security contact - add if available]
2. Describe the vulnerability
3. Provide steps to reproduce
4. Wait for response before disclosure

## 📝 Documentation

### Updating Documentation

Documentation lives in:
- `README.md` - Main documentation
- `MIGRATION.md` - Version migration guides
- `CHANGELOG.md` - Version history
- Docstrings in code

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails

    Example:
        >>> function_name("test", 42)
        True
    """
    ...
```

## 🧪 Testing Guidelines

### Test Organization

```
tests/
├── __init__.py
├── test_connection.py    # Connection tests
├── test_mento.py         # ORM tests
├── test_utils.py         # Utility tests
└── conftest.py          # Shared fixtures
```

### Writing Good Tests

```python
def test_descriptive_name(self):
    """Test description explaining what is being tested."""
    # Arrange
    setup_data = create_test_data()

    # Act
    result = perform_operation(setup_data)

    # Assert
    assert result == expected_value
```

### Test Coverage

- Aim for >90% coverage
- Test happy paths
- Test error conditions
- Test edge cases

## 🎯 Code Quality Standards

### Type Hints

All functions must have type hints:

```python
def insert(
    self,
    table: str,
    data: dict[str, Any],
    check_model: type[BaseModel] | None = None
) -> None:
    ...
```

### Error Handling

- Use specific exceptions
- Provide helpful error messages
- Include context in errors

```python
if not table:
    raise ValueError(f"Table name is required, got: {table}")
```

### Code Organization

- One class per file (for major classes)
- Group related functions
- Keep functions small and focused
- Use descriptive names

## 🔄 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Changelog

Update `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features
```

## 📞 Getting Help

- 💬 [GitHub Discussions](https://github.com/fswair/MentoDB/discussions)
- 🐛 [Issue Tracker](https://github.com/fswair/MentoDB/issues)
- 📖 [Documentation](README.md)

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- README acknowledgments

Thank you for contributing to MentoDB! 🎉
