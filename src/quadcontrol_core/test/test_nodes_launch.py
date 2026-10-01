import time
import unittest

import launch
import launch_ros.actions
import launch_testing
import launch_testing.actions
import rclpy
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import Int32
from std_srvs.srv import SetBool


def generate_test_description():
    # Exercise the installed nodes together through the real ROS graph.
    controller = launch_ros.actions.Node(
        package='quadcontrol_core',
        executable='controller',
        output='screen',
    )
    monitor = launch_ros.actions.Node(
        package='quadcontrol_core',
        executable='monitor',
        output='screen',
    )

    return (
        launch.LaunchDescription(
            [controller, monitor, launch_testing.actions.ReadyToTest()]
        ),
        {'monitor': monitor},
    )


class TestControllerMonitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('counter_integration_test')
        cls.received_values = []

        def record_message(message):
            cls.received_values.append(message.data)

        cls.subscription = cls.node.create_subscription(
            Int32, '/control_counter', record_message, 10
        )
        cls.reset_client = cls.node.create_client(SetBool, '/reset_counter')
        cls.executor = SingleThreadedExecutor()
        cls.executor.add_node(cls.node)

    @classmethod
    def tearDownClass(cls):
        cls.executor.remove_node(cls.node)
        cls.node.destroy_node()
        rclpy.shutdown()

    def _spin_until(self, condition, timeout_sec=5.0):
        # The executor must run to process asynchronous topic and service events.
        deadline = time.monotonic() + timeout_sec
        while not condition() and time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.1)
        self.assertTrue(condition(), 'Timed out waiting for ROS activity')

    def test_controller_publishes_increasing_values(self):
        start_index = len(self.received_values)
        self._spin_until(lambda: len(self.received_values) >= start_index + 2)

        first_value, second_value = self.received_values[
            start_index:start_index + 2
        ]
        self.assertEqual(second_value, first_value + 1)

    def test_reset_service_resets_published_counter(self):
        self.assertTrue(self.reset_client.wait_for_service(timeout_sec=5.0))
        self._spin_until(
            lambda: bool(self.received_values) and self.received_values[-1] > 0
        )
        start_index = len(self.received_values)

        request = SetBool.Request()
        request.data = True
        future = self.reset_client.call_async(request)
        self._spin_until(future.done)
        self.assertTrue(future.result().success)

        self._spin_until(lambda: 0 in self.received_values[start_index:])

    def test_monitor_logs_received_counter(self, proc_output, monitor):
        proc_output.assertWaitFor('Control loop', process=monitor, timeout=5.0)


@launch_testing.post_shutdown_test()
class TestNodesShutdown(unittest.TestCase):
    def test_nodes_exit_cleanly(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
