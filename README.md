# AI
AI server with Langchain

## Installation

### Prerequisites
- Python 3.12 or higher
- Poetry (Python package manager)
- Docker and Docker Compose

### Local Development Setup
1. Clone the repository
```bash
git clone https://github.com/WritelyForWriters/AI.git
cd ai
```

2. Install dependencies with Poetry
```bash
poetry install
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Docker Setup
1. Build and run with Docker Compose
```bash
docker compose -f docker-compose-dev.yml up --build
```

The API server will be available at `http://localhost:8000`

## Development

### Code Quality
This project uses several tools to maintain code quality:
- Ruff for linting and formatting
- MyPy for type checking
- Pre-commit hooks for automated checks

To set up pre-commit hooks:
```bash
poetry run pre-commit install
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.
