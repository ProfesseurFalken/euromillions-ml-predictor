# Contributing to EuroMillions ML Predictor

First off, thank you for considering contributing to this project! 🎉

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment info**: OS, Python version, package versions

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Use case**: Why would this enhancement be useful?
- **Proposed solution**: How should it work?
- **Alternatives considered**: What other solutions have you thought about?

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards below
4. **Test your changes**:
   ```bash
   python -m pytest test_*.py -v
   ```
5. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** against `main`

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Maximum line length: **100 characters**
- Use **docstrings** for all public functions and classes

### Example:

```python
def calculate_frequency(
    numbers: List[int],
    window_size: int = 100
) -> Dict[int, float]:
    """
    Calculate frequency of numbers in the given window.
    
    Args:
        numbers: List of numbers to analyze
        window_size: Number of recent draws to consider
        
    Returns:
        Dictionary mapping each number to its frequency
    """
    # Implementation
    pass
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, semicolons, etc)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Testing

- Write tests for new features
- Ensure all existing tests pass
- Aim for good test coverage

```bash
# Run all tests
python -m pytest test_*.py -v

# Run with coverage
python -m pytest test_*.py --cov=. --cov-report=html
```

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/euromillions-ml-predictor.git
   cd euromillions-ml-predictor
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov  # For testing
   ```

4. Run the application:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## Project Structure

Key files to understand:

| File | Purpose |
|------|---------|
| `config.py` | Configuration management |
| `repository.py` | Database operations |
| `scraper.py` | Web scraping |
| `train_models.py` | ML training |
| `build_datasets.py` | Feature engineering |
| `ui/streamlit_app.py` | Web interface |

## Questions?

Feel free to open an issue with the "question" label if you need help!

---

Thank you for contributing! 🙏
