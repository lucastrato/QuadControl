#include <memory>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>

/**
 * @brief ROS 2 node that monitors the control counter.
 *
 * The Monitor subscribes to the control counter topic and logs each
 * received counter value.
 */
class Monitor : public rclcpp::Node {
public:
  /**
   * @brief Constructs the monitor node.
   *
   * Creates a ROS 2 node named "monitor_node".
   */
  Monitor()
  : Node("monitor_node") {}

  /**
   * @brief Initializes the monitor's ROS 2 interfaces.
   *
   * Creates the subscription to the control counter topic.
   */
  void start()
  {
    subscriber_ = create_subscription<std_msgs::msg::Int32>(
        "/control_counter", 10, [this](const std_msgs::msg::Int32 & message) {
        handle_message(message);
        });
    RCLCPP_INFO(get_logger(), "Monitor started");
  }

private:
  /**
   * @brief Handles a received control counter message.
   *
   * Logs the counter value received from the control counter topic.
   *
   * @param message Message containing the current control counter value.
   */
  void handle_message(const std_msgs::msg::Int32 & message)
  {
    RCLCPP_INFO(get_logger(), "Control loop %d", message.data);
  }

  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr subscriber_;
};

/**
 * @brief Application entry point.
 *
 * Initializes ROS 2, creates and starts the Monitor node, and enters
 * the ROS 2 event loop.
 *
 * @param argc Number of command-line arguments.
 * @param argv Command-line arguments.
 * @return Zero on successful shutdown.
 */
auto main(int argc, char *argv[]) -> int
{
  rclcpp::init(argc, argv);

  auto monitor = std::make_shared<Monitor>();
  monitor->start();
  rclcpp::spin(monitor);

  rclcpp::shutdown();
  return 0;
}
