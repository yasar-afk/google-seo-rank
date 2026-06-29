from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="google-seo-rank",
    version="1.0.0",
    author="yasar-afk",
    description="Google SEO rank tracker and automatic competitor analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yasar-afk/google-seo-rank",
    py_modules=["rank_tracker", "rakip_analiz", "config"],
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "seo-rank=rank_tracker:main",
            "seo-analiz=rakip_analiz:main",
        ],
    },
)
