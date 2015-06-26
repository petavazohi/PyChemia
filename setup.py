from setuptools import setup, find_packages

setup(
    name='pychemia',
    version='0.1.1',
    author='Guillermo Avendano Franco',
    author_email='gtux.gaf@gmail.com',
    packages=find_packages(),
    url='https://github.com/MaterialsDiscovery/PyChemia',
    license='LICENSE.txt',
    description='Python framework for Materials Discovery and Design',
    long_description=open('README.md').read(),
    install_requires=["numpy >= 1.5",
                      "scipy >= 0.9",
                      "matplotlib >= 1.2",
                      "ScientificPython >2.6",
                      'spglib', 'pyspglib', 'qmpy'],
    keywords=["VASP", "ABINIT", "DFTB+", "Octopus", "Fireball", "metaheuristics",
              "electronic", "structure", "analysis", "materials", "discovery"],

)
