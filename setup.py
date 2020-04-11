from distutils.core import setup

setup(
    name='Clock SSE',
    version='1.0',
    description='Clock app for SteelSeries Enginge OLED display',
    author='Aleksei Smyshliaev',
    author_email='aleksei.smyshliaev@gmail.com',
    packages=['clock'],
    package_data={'clock': ['favicon.ico']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Utilities',
    ],
)
