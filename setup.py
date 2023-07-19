from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='spotipy',
    version='0.0.1',
    description='A light weight Python library for the Spotify Web API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@qwiko",
    author_email="jakob.mellberg@gmail.com",
    project_urls={
        'Source': 'https://github.com/Qwiko/badrum',
    },
    install_requires=[
        "spotipy==2.23.0",
        "gpiozero==1.6.2",
    ],
    license='MIT'
)