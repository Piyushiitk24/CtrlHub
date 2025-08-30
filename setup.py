"""
CtrlHub Desktop Agent Setup
Package configuration for pip installation
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("local_agent/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ctrlhub-agent",
    version="1.0.0",
    author="CtrlHub Team",
    author_email="team@ctrlhub.edu",
    description="Desktop agent for CtrlHub control systems education platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Piyushiitk24/CtrlHub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Topic :: Education :: Engineering",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Desktop Environment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ctrlhub-agent=local_agent.main:main",
        ],
    },
    keywords=[
        "control-systems",
        "education", 
        "arduino",
        "simulation",
        "pid-controller",
        "engineering",
        "hardware-in-the-loop",
    ],
    project_urls={
        "Documentation": "https://ctrlhub.edu/docs",
        "Source": "https://github.com/Piyushiitk24/CtrlHub",
        "Tracker": "https://github.com/Piyushiitk24/CtrlHub/issues",
    },
    include_package_data=True,
    package_data={
        "local_agent": [
            "*.py",
            "**/*.py",
            "requirements.txt",
        ],
    },
)