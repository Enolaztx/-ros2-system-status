import socket
import psutil
import rclpy
from rclpy.node import Node
from status_interfaces.msg import SystemStatus


class SysStatusPub(Node):
    """周期性采集系统状态并发布 /sys_status。"""

    def __init__(self):
        super().__init__('sys_status_pub')
        self.publisher_ = self.create_publisher(SystemStatus, 'sys_status', 10)
        self.timer_ = self.create_timer(1.0, self.timer_callback)
        self.hostname = socket.gethostname()

        net = psutil.net_io_counters()
        self._last_sent = net.bytes_sent
        self._last_recv = net.bytes_recv

        psutil.cpu_percent(interval=None)
        self.get_logger().info('SysStatusPub 节点已启动，1 Hz 发布 /sys_status')

    def timer_callback(self):
        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.hostname = self.hostname

        msg.cpu_percent = float(psutil.cpu_percent(interval=None))
        mem = psutil.virtual_memory()
        msg.memory_percent = float(mem.percent)
        msg.memory_total = float(mem.total) / (1024.0 * 1024.0)
        msg.memory_available = float(mem.available) / (1024.0 * 1024.0)

        net = psutil.net_io_counters()
        msg.net_sent = float(net.bytes_sent - self._last_sent) / 1024.0
        msg.net_recv = float(net.bytes_recv - self._last_recv) / 1024.0
        self._last_sent = net.bytes_sent
        self._last_recv = net.bytes_recv

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SysStatusPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
