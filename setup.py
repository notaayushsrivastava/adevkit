from setuptools import setup, find_packages

setup(
    name="adevkit",
    version="0.1.4",
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
    ],
    entry_points={
        "console_scripts": [
            "adevkit=adevkit.cli:main",
            "devkit=adevkit.cli:main",
        ],
    },
)
