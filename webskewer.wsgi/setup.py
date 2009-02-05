from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='webskewer.wsgi',
    version=version,
    description=('WSGI utilities'),
    author='David Hain',
    author_email='dhain@webskewer.org',
    url='http://webskewer.org/',
    license='MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude='tests'),
    namespace_packages=['webskewer'],
)
