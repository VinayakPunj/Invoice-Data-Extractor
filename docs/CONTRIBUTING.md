# Contributing to InvoiceIQ

First off, thank you for considering contributing to InvoiceIQ! It's people like you that make InvoiceIQ such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

**Bug Report Template**:
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 11]
- Python Version: [e.g. 3.11]
- Application Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any potential drawbacks

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message

## Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/VinayakPunj/Invoice-Data-Extractor.git
cd Invoice-Data-Extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Tests

```bash
pytest
```

### 4. Run Application

```bash
streamlit run app.py
```

## Development Guidelines

### Code Style

We follow PEP 8 style guidelines. Before submitting a PR:

```bash
# Format code
black src tests

# Check linting
flake8 src tests

# Type checking (optional)
mypy src
```

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Test edge cases and error conditions
- Use fixtures for common test data

**Test Example**:
```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result == expected_value
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions/classes
- Update ARCHITECTURE.md for structural changes
- Include inline comments for complex logic

**Docstring Format**:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples**:
```
feat(ocr): add support for image files
fix(database): resolve connection leak
docs(readme): update installation instructions
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

## Project Structure

```
Invoice-Data-Extractor/
├── src/              # Source code
├── tests/            # Test suite
├── docs/             # Documentation
├── .github/          # GitHub workflows
├── app.py            # Main application
├── config.py         # Configuration
└── requirements.txt  # Dependencies
```

## Adding New Features

### 1. Create Issue

Open an issue describing the feature and get feedback.

### 2. Implement

- Create a new branch
- Write code following guidelines
- Add tests
- Update documentation

### 3. Test

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_myfeature.py

# Check coverage
pytest --cov=src
```

### 4. Submit PR

- Push to your fork
- Open PR with clear description
- Link related issues
- Wait for review

## Module Development

### Creating a New Module

1. Create file in `src/` directory
2. Add class/functions with docstrings
3. Create corresponding test file
4. Update `__init__.py` if needed
5. Document in ARCHITECTURE.md

**Template**:
```python
"""
Module description.
"""
from typing import Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


class MyClass:
    """Class description."""
    
    def __init__(self, param: str):
        """Initialize."""
        self.param = param
        logger.info("MyClass initialized")
    
    def my_method(self) -> str:
        """Method description."""
        try:
            result = self._process()
            logger.debug(f"Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
```

## Release Process

1. Update version in `src/__init__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create PR to main
6. Tag release after merge
7. Update Docker image

## Getting Help

- Open an issue for questions
- Check existing documentation
- Review closed issues/PRs

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉
