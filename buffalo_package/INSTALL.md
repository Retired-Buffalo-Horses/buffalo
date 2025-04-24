# Buffalo Installation Guide

## Installation via pip

Buffalo is published to PyPI, you can install it directly via pip:

```bash
pip install buffalo-workflow
```

## Installation from Source

If you want to install from source code, you can follow these steps:

### 1. Download or Clone the Source Code

```bash
git clone https://github.com/yourusername/buffalo.git
cd buffalo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the Package

```bash
pip install -e .
```

Or build and install using the following commands:

```bash
python setup.py build
python setup.py install
```

## Development Environment

For developers, it is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install -e .
```

## Verify Installation

After installation, you can verify the installation by running:

```bash
buffalo --help
```

If everything is normal, you will see the help information for the Buffalo command-line tool. 