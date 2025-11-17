try:
    from setuptools import setup, find_packages  # type: ignore
except ImportError:  # pragma: no cover
    from distutils.core import setup  # type: ignore

    def find_packages():  # type: ignore
        return []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="goit-pycore-project",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="CLI bot for managing contacts and notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/goit-pycore-project",
    py_modules=["main", "commands", "contactbook", "notes", "config"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    setup_requires=["setuptools>=40.0.0"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cli-bot=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
