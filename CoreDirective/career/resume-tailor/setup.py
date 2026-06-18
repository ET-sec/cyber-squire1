from setuptools import setup, find_packages

setup(
    name="resume-tailor",
    version="1.0.0",
    description="CLI tool to tailor resumes, cover letters, and research briefs from job postings",
    author="Emmanuel Tigoue",
    author_email="emmanueltigoue@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "resume_tailor": ["templates/*.j2"],
    },
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "click>=8.1.0",
        "jinja2>=3.1.0",
        "anthropic>=0.40.0",
        "rich>=13.0.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "resume-tailor=resume_tailor.cli:main",
        ],
    },
    python_requires=">=3.11",
)
