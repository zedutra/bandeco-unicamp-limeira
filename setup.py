from setuptools import find_packages, setup

setup(
    name="bandeco",
    version="1.1.0",
    description="Aplicação de linha de comando para verificar o cardápio do RU da Unicamp Limeira",
    author="zedutra",
    author_email="zedutra@protonmail.com",
    url="https://github.com/zedutra/bandeco-unicamp-limeira",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "bandeco=bandeco.bandeco:main",
        ],
    },
    python_requires=">=3.8",
)
