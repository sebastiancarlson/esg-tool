from setuptools import setup, find_packages

setup(
    name="gemini-cli-tool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "typer[all]",
        "rich",
        "python-dotenv",
        "pillow"
    ],
    entry_points={
        "console_scripts": [
            "gemini=gemini_cli.main:app",
        ],
    },
)
