# New Python Development Environment

This workspace is set up for Python development.

## Included files

- `.gitignore` - excludes environment artifacts and cache files
- `requirements.txt` - list of dependencies
- `main.py` - sample application entry point
- `tests/test_main.py` - sample unit test
- `.vscode/` - VS Code launch and workspace settings

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

### Sample CLI app

```powershell
python main.py
```

### Real estate website

Install dependencies, then run:

```powershell
python app.py
```

The app creates a local SQLite database file named `realestate.db` in the workspace root the first time it runs.

Open `http://127.0.0.1:5000` in your browser.

## Test

```powershell
python -m unittest discover tests
```

## Pytest

Install test dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run pytest:

```powershell
python -m pytest
```
