# Contributing to Earning Robot

Thank you for your interest in contributing to the Earning Robot project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/robot.git
cd robot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Copy example env
cp .env.example .env
# Edit .env with test credentials

# Run tests
pytest tests/ -v
```

## How to Contribute

### Reporting Bugs

Use GitHub Issues to report bugs. Include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant logs or error messages

**Example:**
```
Title: API returns 500 on invalid task ID

Description:
When calling GET /api/task/{task_id} with an invalid ID,
the API returns 500 instead of 404.

Steps to Reproduce:
1. Start the server
2. Call: curl http://localhost:5000/api/task/99999
3. Observe 500 error

Expected: 404 Not Found
Actual: 500 Internal Server Error

Environment: Ubuntu 22.04, Python 3.10
```

### Suggesting Features

Use GitHub Issues with the "enhancement" label. Include:

- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Any breaking changes

### Contributing Code

1. **Pick an Issue**: Look for issues tagged "good first issue" or "help wanted"
2. **Comment**: Let others know you're working on it
3. **Create Branch**: Use descriptive names
4. **Write Code**: Follow coding standards
5. **Test**: Add tests for new features
6. **Document**: Update docs as needed
7. **Submit PR**: Create a pull request

## Coding Standards

### Python Style

Follow PEP 8 style guide:

```python
# Good
def calculate_profit(income, expenses):
    """Calculate net profit from income and expenses."""
    return income - expenses

# Bad
def calc(i,e):
    return i-e
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

```python
# Good
class AIProvider:
    MAX_RETRIES = 3
    
    def __init__(self):
        self._api_key = None
    
    def generate_response(self, prompt):
        pass

# Bad
class ai_provider:
    maxRetries = 3
    
    def GenerateResponse(self, prompt):
        pass
```

### Docstrings

Use clear docstrings for all public functions:

```python
def create_task(prompt, provider='openai'):
    """
    Create and execute an AI task.
    
    Args:
        prompt (str): The user's question or request
        provider (str): AI provider name (default: 'openai')
        
    Returns:
        dict: Task result with response, cost, and metadata
        
    Raises:
        ValueError: If provider is invalid
        APIError: If AI API call fails
    """
    pass
```

### Imports

Organize imports in this order:

```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import requests
from flask import Flask

# Local
from backend.config import Config
from backend.database import Database
```

### Error Handling

Always handle errors gracefully:

```python
# Good
try:
    result = ai_provider.generate_response(prompt)
    return result
except APIError as e:
    logger.error(f"API error: {e}")
    return {'error': 'Service temporarily unavailable'}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {'error': 'An error occurred'}

# Bad
result = ai_provider.generate_response(prompt)  # May crash
return result
```

### Logging

Use appropriate log levels:

```python
import logging

logger = logging.getLogger(__name__)

# Debug: Detailed diagnostic info
logger.debug(f"Request payload: {data}")

# Info: General informational messages
logger.info("Task completed successfully")

# Warning: Something unexpected but not critical
logger.warning("API rate limit approaching")

# Error: Error occurred but app continues
logger.error(f"Failed to process task: {e}")

# Critical: Serious error, app may not continue
logger.critical("Database connection lost")
```

## Testing

### Writing Tests

All new features should include tests:

```python
import pytest
from backend.database import Database, Task

def test_create_task():
    """Test task creation"""
    db = Database(':memory:').initialize()
    session = db.get_session()
    
    task = Task(
        task_type='test',
        ai_provider='openai',
        input_text='Test question',
        status='pending'
    )
    session.add(task)
    session.commit()
    
    # Verify
    retrieved = session.query(Task).first()
    assert retrieved is not None
    assert retrieved.task_type == 'test'
    
    session.close()
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_basic.py -v

# Run with coverage
pytest tests/ --cov=backend --cov=billing

# Run specific test
pytest tests/test_basic.py::test_create_task -v
```

### Test Coverage

Aim for 80%+ code coverage for new features.

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No unnecessary changes
- [ ] Commit messages are clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### PR Review Process

1. **Submit PR**: Create pull request with clear description
2. **CI Checks**: Wait for automated tests to pass
3. **Code Review**: Maintainers will review your code
4. **Address Feedback**: Make requested changes
5. **Approval**: Once approved, PR will be merged
6. **Celebrate**: Your contribution is now part of the project! 🎉

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for Mistral AI provider"
git commit -m "Fix: Handle 404 errors in task endpoint"
git commit -m "Docs: Update API documentation with examples"

# Bad
git commit -m "Fix bug"
git commit -m "Changes"
git commit -m "WIP"
```

## Development Workflow

### Feature Development

```bash
# Create feature branch
git checkout -b feature/add-gemini-support

# Make changes
# ... code ...

# Run tests
pytest tests/ -v

# Commit
git add .
git commit -m "Add Gemini AI provider support"

# Push
git push origin feature/add-gemini-support

# Create PR on GitHub
```

### Bug Fix

```bash
# Create fix branch
git checkout -b fix/task-404-error

# Fix the bug
# ... code ...

# Add test that would have caught the bug
# ... test code ...

# Verify fix
pytest tests/ -v

# Commit
git commit -m "Fix: Return 404 for invalid task IDs"

# Push and create PR
git push origin fix/task-404-error
```

## Areas for Contribution

### High Priority

- [ ] Web dashboard UI
- [ ] More AI provider integrations
- [ ] Enhanced security features
- [ ] Performance optimizations
- [ ] Extended test coverage

### Good First Issues

- [ ] Add more example scripts
- [ ] Improve error messages
- [ ] Add input validation
- [ ] Documentation improvements
- [ ] Code cleanup and refactoring

### Advanced Features

- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Metrics and monitoring
- [ ] Multi-language support

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our community (if available)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing to Earning Robot! 🚀
