from setuptools import setup, find_packages

setup(
    name="aayush-devkit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.0.0",
        "inquirerpy>=0.3.4",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "devkit=devkit.cli:main",
        ],
    },
)
