from setuptools import setup, find_packages

setup(
    name="token_client",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "web3",
        "flask",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
) 