from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="buffalo-workflow",  # package name, avoid conflicts with existing packages
    version="0.1.0",
    author="Buffalo Team",
    author_email="your.email@example.com",
    description="A workflow management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Retired-Buffalo-Horses/buffalo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml"
    ],
    package_data={
        'buffalo': ['templates/wf_template.yml'],
    },
    include_package_data=True,
)
