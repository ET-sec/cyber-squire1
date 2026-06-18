from setuptools import setup, find_packages

setup(
    name="proposal-gen",
    version="1.0.0",
    description="Professional consulting proposal generator with Claude AI and branded PDF output",
    author="Emmanuel Tigoue",
    author_email="emmanueltigoue@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "anthropic>=0.40.0",
        "reportlab>=4.0.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "proposal-gen=proposal_gen.cli:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
