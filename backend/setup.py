from setuptools import setup, find_packages
from ssr import __version__

setup(
    name='Spiral Session Recorder',
    version=__version__,

    author='Christian Späth',
    author_email='mail@cspaeth.de',

    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/manage.py'],

    install_requires=(
        'django'
    )
)
