import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="roxar_api_utils",
    version="0.0.1",
    author="Stein Gulbrandsen",
    author_email="stein.gulbrandsen@emerson.com",
    description="Common utility functions that can be used to supplement the Roxar API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoxarAPI/roxar_api_utils",
    project_urls={
        "Bug Tracker": "https://github.com/RoxarAPI/roxar_api_utils/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["roxar_api_utils.wells"],
    python_requires=">=3.7",
)
