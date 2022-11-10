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

Copy .env.default file to .env and override there.
```
cp .env.default .env
```

Also install [flake8](https://github.com/PyCQA/flake8) locally.

### Vim users
Set python3 provider and have `pynvim` installed globally.


### Missing imports or stubs
If there is any library causing mypy to fail saying no stubs found, add the following to `mypy.ini`:
```
[mypy-<package_name>.*]
ignore_missing_imports = True
```

**NOTE:** Run vim after activating poetry env by running `poetry shell`
