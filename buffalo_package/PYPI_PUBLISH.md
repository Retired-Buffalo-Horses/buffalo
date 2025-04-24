# Guide to Publishing on PyPI

Below are the steps to publish the Buffalo package to PyPI.

## Preparation

1. Make sure you have installed the necessary tools:

```bash
pip install build twine
```

2. Make sure you have a PyPI account, if not, please register an account at [https://pypi.org/account/register/](https://pypi.org/account/register/).

## Build Distribution Packages

Execute the following in the project root directory (the directory containing setup.py):

```bash
python -m build
```

This will create two distribution files: a wheel file (.whl) and a source distribution file (.tar.gz), in the `dist/` directory.

## Check Distribution Packages

Make sure the contents of the distribution packages are correct:

```bash
twine check dist/*
```

## Upload to PyPI

First, you can try uploading to the test version of PyPI:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

If everything is normal, then upload to the official version of PyPI:

```bash
twine upload dist/*
```

Both commands will require you to enter your PyPI username and password.

## Verify Installation

Install your package from PyPI to verify the publishing was successful:

```bash
pip install --index-url https://test.pypi.org/simple/ buffalo-workflow  # Install from test PyPI
pip install buffalo-workflow  # Install from official PyPI
```

## Update Version

When you need to publish a new version, please update the `__version__` variable (in the `buffalo/__init__.py` file) and the version number in `setup.py`, then repeat the above steps. 