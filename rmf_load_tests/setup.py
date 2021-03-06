from glob import glob
from setuptools import setup

package_name = 'rmf_load_tests'

setup(
    name=package_name,
    version='0.0.0',
    packages=['rmf_load_tests'],
    py_modules=[],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*')),
    ],
    install_requires=['setuptools'],
    author='Morgan Quigley',
    author_email='morgan@osrfoundation.org',
    zip_safe=True,
    maintainer='Morgan Quigley',
    maintainer_email='morgan@osrfoundation.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='rmf_test_map_tools',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'endless_work = rmf_load_tests.endless_work:main',
        ],
    },
)
