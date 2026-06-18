from setuptools import setup, find_packages

setup(
    name="content-repurpose",
    version="1.0.0",
    description="Repurpose long-form content into platform-optimized posts using Claude AI",
    author="CoreDirective",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "click>=8.1.0",
        "anthropic>=0.40.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "content-repurpose=content_repurpose.cli:main",
        ],
    },
)
