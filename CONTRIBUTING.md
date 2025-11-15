# Contributing to smartratelimit

Thank you for your interest in contributing to smartratelimit! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartratelimit
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev,all]"
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use `black` for code formatting:
  ```bash
  black smartratelimit/ tests/
  ```

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Run tests before submitting:
  ```bash
  pytest tests/ -v --cov=smartratelimit
  ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Code Review

- All code must be reviewed before merging
- Address review comments promptly
- Keep PRs focused and reasonably sized

## Reporting Bugs

When reporting bugs, please include:
- Python version
- Library version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/tracebacks

## Feature Requests

Feature requests are welcome! Please:
- Check if the feature already exists
- Explain the use case
- Describe the expected behavior
- Consider implementation complexity

## Questions?

Feel free to open an issue for questions or discussions.

