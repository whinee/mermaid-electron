# regex to match recipe names and their comments:
# ^    (?P<recipe>\S+)(?P<args>(?:\s[^#\s]+)*)(?:\s+# (?P<docs>.+))*

# Constants
purple_msg := '\e[38;2;151;120;211m%s\e[0m'
time_msg := '\e[38;2;151;120;211m%s\e[0m: %.2fs\n'

# Derived Constants
cwd := `python -c 'import os;print(os.getcwd())'`
system_python := if os_family() == "windows" { "py.exe -3.10" } else { "python3.10" }
pyenv_dir := cwd + if os_family() == "windows" { "\\pyenv" } else { "/pyenv" }
pyenv_bin_dir := pyenv_dir + if os_family() == "windows" { "\\Scripts" } else { "/bin" }
python := pyenv_bin_dir + if os_family() == "windows" { "\\python.exe" } else { "/python3" }
pyenv_activate := pyenv_bin_dir + if os_family() == "windows" { "\\Activate.ps1" } else { "/activate" }

# Choose recipes
default:
    @ just -lu; printf '%s ' press Enter to continue; read; just --choose

# n1 - n2
[private]
minus n1 n2:
    @ python -c 'print(round({{n1}} - {{n2}}, 2))'

# Time commands
[private]
time msg err *cmd:
    #!/usr/bin/env bash
    printf '{{purple_msg}}: ' 'cmd'; printf '%s ' {{cmd}}; echo
    cs=$(date +%s.%N)
    if {{cmd}}; then
        printf '{{time_msg}}' '{{msg}}' "$(just minus $(date +%s.%N) $cs)"
    else
        printf '{{time_msg}}' '{{err}}' "$(just minus $(date +%s.%N) $cs)"
    fi

# Time commands without saying command name
[private]
time_nc msg err *cmd:
    #!/usr/bin/env bash
    cs=$(date +%s.%N)
    if {{cmd}}; then
        printf '{{time_msg}}' '{{msg}}' "$(just minus $(date +%s.%N) $cs)"
    else
        printf '{{time_msg}}' '{{err}}' "$(just minus $(date +%s.%N) $cs)"
    fi

[private]
[unix]
b64e file:
    base64 -w0 {{file}}

[private]
ruff:
    @ {{ python }} -m ruff check . --fix; exit 0

# Set up development environment
bootstrap:
    #!/usr/bin/env bash
    rm -rf poetry.lock
    if test ! -e pyenv; then
        {{ system_python }} -m venv pyenv
        source {{pyenv_activate}}
    fi
    {{ python }} -m pip install --upgrade pip poetry
    {{ python }} -m poetry install --with dev
    {{ python }} -m pip cache purge
    yarn install

# Lint codebase
lint:
    @ just time "          Python Files Formatted" "  Formatting Python Files Failed" {{ python }} -m black -q .
    @ just time "             Python Files Linted" "     Linting Python Files Failed" just ruff

push:
    git add .
    git commit -m "push"
    git push -u origin main

build:
    yarn electron-builder
