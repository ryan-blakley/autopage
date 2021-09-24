from setuptools import find_packages, setup

data_files = [
    (f"share/licenses/python-autopage", ['LICENSE'])
]

if __name__ == "__main__":
    setup(
        name='autopage',
        description='A library to provide automatic paging for console output',
        author='Zane Bitter',
        author_email='zbitter@redhat.com',
        version="0.4.1",
        packages=find_packages(),
        include_package_data=True,
        classifiers=[
            'License :: OSI Approved',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Operating System :: POSIX',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Terminals',
            'Topic :: Utilities'
        ],
        data_files=data_files
    )

