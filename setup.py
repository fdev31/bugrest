from codecs import open
from setuptools import setup

setup(
    name="bugrest",
    version="1.0",
    author="Fabien Devaux",
    author_email="fdev31@gmail.com",
    license="MIT",
    packages=['bugrest'],
    include_package_data=True,
    package_data={'bugrest': ['*.css']},
    description="Simple CLI bugtracker using standard ReStructuredtext",
    long_description=open('README.rst', encoding='utf-8').read(),
    scripts=['br'],
    url='https://github.com/fdev31/bugrest',
    keywords=[],
    install_requires=[
        'docutils >= 0.12',
        ],
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
