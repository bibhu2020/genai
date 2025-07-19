from setuptools import setup

setup(
    name='ml_000',
    version='0.1',
    description='A simple machine learning package',
    author='Bibhu Mishra',
    author_email="bm801777@gmail.com",
    packages=['package.feature','package.ml_training'],
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)


