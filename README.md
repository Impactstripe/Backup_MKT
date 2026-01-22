Project start instructions

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m package_one.main
```

Alternative (uses the script entry from `pyproject.toml`):

```powershell
.\.venv\Scripts\my-script
```

Notes:
- Ensure the virtual environment is activated or use the full path to the venv Python shown above.
- If `PyQt6` is missing, install dependencies from `pyproject.toml` into the venv, e.g. `pip install PyQt6==6.10.2 PyQt6-Qt6==6.10.1 PyQt6_sip==13.10.3`.

