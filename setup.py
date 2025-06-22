from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-framework",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for creating web automation agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agent-framework",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
