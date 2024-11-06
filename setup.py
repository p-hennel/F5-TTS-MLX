from setuptools import setup

setup(
    name='f5tts',
    version='0.1.0',
    py_modules=['main', 'content', 'tts'],
    install_requires=[
        'Click',
        'click-default-group',
        'f5-tts-mlx',
        'soundfile',
        'tqdm',
        'nltk'
    ],
    entry_points={
        'console_scripts': [
            'f5tts = main:cli',
        ],
    },
)