from setuptools import setup, find_packages
import os

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="osint-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive OSINT framework for security research and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/osint-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.18.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'mypy>=0.950',
            'flake8>=4.0.0',
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.18.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'osint-scan=osint.framework:main',
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/osint-framework/issues",
        "Documentation": "https://osint-framework.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/osint-framework",
    },
    include_package_data=True,
    package_data={
        'osint': ['config/*.yaml'],
    },
    zip_safe=False,
)
