from setuptools import setup, find_packages

description = "VT-100 terminal implementation of the card game Spite and Malice."
setup(
    name="sciibo",
    version="0.8.0",
    url="https://github.com/fdev/sciibo",
    download_url="https://github.com/fdev/sciibo/tarball/master",
    license="MIT",
    description=description,
    long_description=description,
    author="Folkert de Vries",
    author_email="sciibo@fdev.nl",
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    sciibo = sciibo:play
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment :: Board Games",
    ]
)
