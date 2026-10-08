# ROS2 System Status Monitor

ROS2 系统状态监控：一个节点采集并发布系统状态，另一个节点用 Qt 实时显示。

## 构建

colcon build
source install/setup.bash

## 运行

ros2 run status_publisher sys_status_pub
ros2 run status_publisher sys_status_display
