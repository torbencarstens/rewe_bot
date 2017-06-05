from distutils.core import setup

setup(
    name='rewe_bot',
    version='0.0.1',
    packages=[''],
    url='https://github.com/Chabare/rewe_bot',
    license='MIT',
    author='chabare',
    author_email='chabare95@gmail.com',
    description=''

    entry_points = {
        "": [
            "rewe_bot = rewe_bot.__main__:main",
        ],
    }
)
