from setuptools import setup

package_name = 'status_publisher'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'psutil', 'PyQt5'],
    zip_safe=True,
    maintainer='dev',
    maintainer_email='dev@example.com',
    description='发布系统状态并通过 Qt 显示',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sys_status_pub     = status_publisher.sys_status_pub:main',
            'sys_status_display = status_publisher.sys_status_display:main',
        ],
    },
)
