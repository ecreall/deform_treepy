import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'deform'
    ]

testing_extras = ['nose', 'coverage', 'beautifulsoup4']

setupkw = dict(
    name='deform_treepy',
    version='1.0.1',
    description='A tree widget for deform',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        ],
    author='Amen Souissi',
    author_email="amensouissi@ecreall.com",
    url='https://github.com/ecreall/deform_treepy/',
    keywords='web forms form tree widget',
    license="AGPLv3+",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=testing_extras,
    install_requires=requires,
    test_suite="deform_treepy",
    extras_require = {
        'testing':testing_extras,
        },
    )

# to update catalogs, use babel and lingua !
try:
    import babel
    babel = babel # PyFlakes
    # if babel is installed, advertise message extractors (if we pass
    # this to setup() unconditionally, and babel isn't installed,
    # distutils warns pointlessly)
    setupkw['message_extractors'] = { "deform_treepy": [
        ("**.py",     "lingua_python", None ),
        ("**.pt", "lingua_xml", None ),
        ]}
except ImportError:
    pass

setup(**setupkw)
