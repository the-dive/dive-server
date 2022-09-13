## Setting up Local Development

Install [pyenv](https://github.com/pyenv/pyenv) and  [poetry](https://github.com/python-poetry/poetry) 

Install python version in `pyproject.toml` which is `3.10.6`:
```
pyenv install 3.10.6
```
Install dependencies:
```
poetry install
```

Also install [flake8](https://github.com/PyCQA/flake8) locally.

### Vim users
Set python3 provider and have `pynvim` installed globally.

**NOTE:** Run vim after activating poetry env by running `poetry shell`
