from setuptools import find_packages, setup

package_name = 'treasure_robot_sensor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cbj',
    maintainer_email='cbj@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'line_follow_node = treasure_robot_sensor.line_follow_node:main',
            'scan_node = treasure_robot_sensor.scan_node:main',
        ],
    },
)
