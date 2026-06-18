from setuptools import setup, find_packages

setup(
    name="job-digest",
    version="1.0.0",
    description="Cybersecurity job posting scraper, scorer, and digest generator",
    author="ET",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "feedparser>=6.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0.0",
        "schedule>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "job-digest=job_digest.cli:main",
        ],
    },
    python_requires=">=3.11",
)
