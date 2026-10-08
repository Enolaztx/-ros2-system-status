import sys
import threading
import datetime

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor

from status_interfaces.msg import SystemStatus

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QGroupBox,
)


class RosBridge(QObject):
    status_received = pyqtSignal(object)


class StatusSubscriber(Node):
    def __init__(self, bridge):
        super().__init__('sys_status_display')
        self.bridge = bridge
        self.create_subscription(SystemStatus, 'sys_status', self._on_msg, 10)

    def _on_msg(self, msg):
        self.bridge.status_received.emit(msg)


class StatusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('系统状态监控 (ROS2)')
        self.resize(440, 340)

        root = QVBoxLayout(self)
        group = QGroupBox('实时状态')
        grid = QGridLayout(group)

        self.labels = {}
        rows = [
            ('stamp',            '时间'),
            ('hostname',         '主机名'),
            ('cpu_percent',      'CPU 使用率 (%)'),
            ('memory_percent',   '内存使用率 (%)'),
            ('memory_total',     '内存总大小 (MB)'),
            ('memory_available', '剩余内存 (MB)'),
            ('net_sent',         '网络发送 (KB/s)'),
            ('net_recv',         '网络接收 (KB/s)'),
        ]
        for i, (key, text) in enumerate(rows):
            grid.addWidget(QLabel(f'{text}:'), i, 0)
            v = QLabel('--')
            v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            v.setMinimumWidth(180)
            grid.addWidget(v, i, 1)
            self.labels[key] = v

        root.addWidget(group)
        root.addStretch(1)

    def update_status(self, msg):
        t = msg.stamp.sec + msg.stamp.nanosec * 1e-9
        dt = datetime.datetime.fromtimestamp(t)
        self.labels['stamp'].setText(dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        self.labels['hostname'].setText(msg.hostname)
        self.labels['cpu_percent'].setText(f'{msg.cpu_percent:.2f}')
        self.labels['memory_percent'].setText(f'{msg.memory_percent:.2f}')
        self.labels['memory_total'].setText(f'{msg.memory_total:.2f}')
        self.labels['memory_available'].setText(f'{msg.memory_available:.2f}')
        self.labels['net_sent'].setText(f'{msg.net_sent:.2f}')
        self.labels['net_recv'].setText(f'{msg.net_recv:.2f}')


def main(args=None):
    rclpy.init(args=args)

    app = QApplication(sys.argv)
    window = StatusWindow()

    bridge = RosBridge()
    node = StatusSubscriber(bridge)
    bridge.status_received.connect(window.update_status, Qt.QueuedConnection)

    executor = SingleThreadedExecutor()
    executor.add_node(node)
    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    window.show()
    try:
        ret = app.exec_()
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(ret)


if __name__ == '__main__':
    main()
