#include <memory>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>

class Monitor : public rclcpp::Node {
public:
  Monitor()
  : Node("monitor_node") {}

  void start()
  {
    subscriber_ = create_subscription<std_msgs::msg::Int32>(
        "/control_counter", 10, [this](const std_msgs::msg::Int32 & message) {
        handle_message(message);
        });
    RCLCPP_INFO(get_logger(), "Monitor started");
  }

private:
  void handle_message(const std_msgs::msg::Int32 & message)
  {
    RCLCPP_INFO(get_logger(), "Control loop %d", message.data);
  }

  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr subscriber_;
};

auto main(int argc, char *argv[]) -> int
{
  rclcpp::init(argc, argv);

  auto monitor = std::make_shared<Monitor>();
  monitor->start();
  rclcpp::spin(monitor);

  rclcpp::shutdown();
  return 0;
}
