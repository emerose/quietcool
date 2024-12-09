from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quietcool",
    version="0.1.1",
    author="Sam Quigley",
    author_email="quigley@emerose.com",
    description="A Python client for controlling QuietCool Wireless RF Control Kit fans via BLE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emerose/quietcool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "bleak>=0.21.1",
    ],
    entry_points={
        "console_scripts": [
            "quietcool=quietcool:main",
        ],
    },
)
