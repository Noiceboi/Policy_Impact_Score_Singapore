#!/usr/bin/env python3
"""Setup script for Policy Impact Assessment Framework."""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Get version from src/__init__.py
version_dict = {}
with open(here / "src" / "__init__.py") as f:
    exec(f.read(), version_dict)

setup(
    name="policy-impact-assessment-singapore",
    version=version_dict["__version__"],
    description="A comprehensive framework for evaluating Singapore government policy impacts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Noiceboi/Policy_Impact_Score_Singapore",
    author=version_dict["__author__"],
    author_email=version_dict["__email__"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="policy, impact, assessment, singapore, mcda, government, analysis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "jinja2>=3.0.0",
        "requests>=2.25.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
        "pandera>=0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "pylint>=2.10",
            "bandit>=1.7",
            "pip-audit>=2.0",
            "pre-commit>=2.15",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "policy-assessment=policy_impact.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Noiceboi/Policy_Impact_Score_Singapore/issues",
        "Source": "https://github.com/Noiceboi/Policy_Impact_Score_Singapore",
        "Documentation": "https://noiceboi.github.io/Policy_Impact_Score_Singapore/",
    },
)
