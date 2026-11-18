# Project-ZeroWord

Python-based Secure Password Manager

## Setup

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh             # Download UV as a python manager
uv --version                                                # Verify install worked

git clone git@github.com:tcolehowell/Project-ZeroWord.git   # Clone repo
cd Project-ZeroWord                                         # Move to project folder

uv sync                                                     # Sets up the python interperter and downloads all the packages
source .venv/bin/activate                                   # Activates the virtual environment to run the program

uv run project-zeroword                                     # Runs main program
```

### Windows (Powershell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"      # Download UV as python manager
uv --version                                                                            # Verify install worked

git clone git@github.com:tcolehowell/Project-ZeroWord.git                               # Clone repo
cd Project-ZeroWord                                                                     # Move to project folder

uv sync                                                                                 # Sets up the python interperter and downloads all the packages
.venv\Scripts\activate                                                                  # Activates the virtual environment to run the program

uv run project-zeroword                                                                 # Runs main program
```

## Adding or removing packages

```bash
uv add <package>          # add a package the app needs
uv add --dev <package>    # add a dev-only tool (e.g. pytest)
uv remove <package>       # remove a package
```
