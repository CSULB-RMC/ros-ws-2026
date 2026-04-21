from setuptools import find_packages, setup

package_name = 'teleop'

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
    maintainer='leopan',
    maintainer_email='leo.long.pan@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'driver_station = teleop.driver_station:main',
            'teleop_drive = teleop.teleop_drive:main',
            'rover_gui = teleop.gui_node:main',
        ],
    },
)
