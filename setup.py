from setuptools import setup, find_packages

setup(
    name="adevkit",
    version="0.1.5",
    author="Aayush Srivastava",
    author_email="contact@aayushsrivastava.com",
    url="https://aayushsrivastava.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.*", "**/*", "**/**/*"],
    },
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.0.0",
        "inquirerpy>=0.3.4",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "reactpy[fastapi]>=1.1.0",
        "uvicorn>=0.29.0",
        "pywebview>=5.0.0",
    ],
    extras_require={
        "gui": [
            "reactpy[fastapi]>=1.1.0",
            "uvicorn>=0.29.0",
            "pywebview>=5.0.0",
        ],
        "cli": [],
        "all": [
            "reactpy[fastapi]>=1.1.0",
            "uvicorn>=0.29.0",
            "pywebview>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "adevkit=adevkit.cli.main:main",
            "devkit=adevkit.cli.main:main",
        ],
    },
)
