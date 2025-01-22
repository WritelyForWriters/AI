# Contributing to AI

## Development Process
We follow the GitHub Flow branching strategy and use conventional commits for clear communication.

### Branching Strategy
1. Create a new branch from `main` for each feature/fix
```bash
git checkout -b <type>/<description>
# Example: git checkout -b feat/add-user-auth
```

2. Make your changes and commit using conventional commit messages
3. Push your branch and create a Pull Request

### Commit Message Convention
Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `style`: Changes that do not affect the meaning of the code
- `docs`: Documentation only changes
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `perf`: Performance improvements

Examples:
```
feat: add JWT authentication
fix: handle null response in user endpoint
docs: update installation guide
```

### Pull Request Process
1. Ensure your code follows the project's style guide
2. Update documentation if needed
3. Make sure all tests pass and add new ones if necessary
4. Get at least one code review approval
5. Squash and merge your commits when approved

### Development Workflow
1. Pick an issue or create one for your work
2. Create a feature branch
3. Write code and tests
4. Run quality checks locally
```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy .
```
5. Create a Pull Request

### Code Review Guidelines
- Keep changes focused and small
- Write clear PR descriptions
- Respond to review comments promptly
- Request reviews from relevant team members

## Bug Reports
We use GitHub issues to track public bugs. Report a bug by opening a new issue.

### Write bug reports with detail, background, and sample code
- A quick summary and/or background
- Steps to reproduce
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License. 