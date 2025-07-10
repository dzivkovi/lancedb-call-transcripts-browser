# Contributing to the Project

Thank you for considering contributing to this project! This guide outlines the process for contributing and the standards we follow.

## Development Environment Setup

### Project Setup

1. **Clone the repository**

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   
   # Install development tools
   pip install ruff pytest
   ```

## Development Workflow

### Evaluation-First Development

We follow strict TDD principles, especially important for AI-assisted development:

1. **Write failing tests first** that demonstrate the bug or required feature
   - Tests are immutable - no changing them to make implementation easier!
   - Include edge cases and run multiple times (5+ runs) to catch nondeterminism
2. **Implement the minimum code** necessary to make tests pass
   - Let tests guide implementation, not vice versa
3. **Refactor** while keeping tests passing
   - Performance optimization only after correctness

**Example workflow:**

```python
# 1. Write test (MUST fail initially)
# 2. Run test - verify it fails
# 3. Implement solution
# 4. Run test 5+ times - verify consistent passes
# 5. Only then create PR
```

### Coding Standards

- **Python**: Follow [PEP 8](https://peps.python.org/pep-0008/) style guide (120 char line length)
- **Docstrings**: Use [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings
- **Code Quality**: Run `ruff check` and `ruff format` before committing

  ```bash
  ruff format .         # Formatting (replaces black)
  ruff check .          # Linting (replaces flake8, pylint, and more)
  ```

- **Configuration**: See `pyproject.toml` for project-specific settings

### Cypher Query Standards

- Indent and format queries for readability
- Use parameters instead of string concatenation
- Include execution plan analysis for complex queries
- Document any index requirements

## Pull Request Process

* **Branches & titles**: Use `feat|fix|docs|chore/<issue#>-slug` for branches and the same `feat:` / `fix:` / `docs:` / `chore:` prefix in commit headers and issue titles.

1. **Create a branch** for your feature or fix

   ```bash
   git checkout -b feat/123-add-new-feature
   # or: fix/456-bug-description
   # or: docs/789-update-readme  
   # or: chore/101-cleanup-code
   ```

2. **Implement your changes** following TDD approach

3. **Run code quality checks**

   ```bash
   ruff format .        # Format code
   ruff check . --fix   # Auto-fix what's possible
   ```

4. **Ensure all tests pass**

   ```bash
   pytest
   ```

5. **Submit a PR** with a clear description:
   - What problem does it solve?
   - How was it tested?

## Documentation

- Update README.md if introducing new features
- Document any new models or relationships
- Provide example usage in docstrings
- Include performance considerations for graph operations

## Graph Data Considerations

- Consider scalability implications of graph model changes
- Document any new indexes or constraints
- Be mindful of memory usage in complex traversals
- Include test data where appropriate

---

Remember: "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
