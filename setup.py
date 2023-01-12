from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="thelofiwipystation",
    version="0.0.1",
    description="thelofiwipystation",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/kiasamouie/thelofiwipystation",
    author="Kia Samouie",
    author_email="thekiadoe@gmail.com",
    keywords="thelofiwipystation",
    license="MIT",
    packages=["lofiwifi"],
    install_requires=['moviepy','youtube-dl','eyed3','pysimplegui'],
    include_package_data=True,
)
