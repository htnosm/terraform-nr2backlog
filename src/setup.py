from setuptools import setup, find_packages


def read_requirements(file):
    with open(file, 'r') as f:
        return f.read().splitlines()


setup(
    name="nr2backlog",
    packages=find_packages(),
    #install_requires=read_requirements('requirements.txt'),
    extras_require={
        "develop": [
            'pytest==8.3.2',
            'pytest-cov==5.0.0',
            'moto==5.0.12',
        ]
    },
)
