import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metrobus",
    version="0.0.7",
    author="Chris Fauerbach",
    author_email="chris@fauie.com",
    description="A package to allow flexible and quick programs on a message bus/kafka.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisfauerbach/metrobus",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

