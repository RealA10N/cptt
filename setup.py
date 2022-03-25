from setuptools import setup, find_packages
import cptt

with open("README.md", encoding="utf8") as f:
    README = f.read()

with open("CHANGELOG.md", encoding="utf8") as f:
    CHANGELOG = f.read()

with open("requirements.txt", encoding="utf8") as f:
    DEPENDENCIES = f.read().splitlines()

setup(
    name="cptt",
    version=cptt.__version__,
    description=cptt.__description__,
    url='https://github.com/RealA10N/cptt',

    python_requires=">=3.7,<4",
    install_requires=DEPENDENCIES,

    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type="text/markdown",

    author=cptt.__author__,
    author_email=cptt.__author_email__,

    packages=find_packages(include=['cptt*']),
)
