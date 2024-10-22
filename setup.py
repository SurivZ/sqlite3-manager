from setuptools import setup, find_packages

setup(
    name='sqlite3-manager',
    version='1.0.1',
    author='SurivZ',
    author_email='franklinserrano23@email.com',
    description='Este paquete proporciona una serie de funcionalidades para gestionar bases de datos SQLite3 de manera sencilla y estandarizada.',
    long_description=open('./readme.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SurivZ/sqlite3-manager',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.10',
    install_requires=[],
    entry_points={
        'console_scripts': [],
    },
)
