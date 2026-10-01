#include <chrono>
#include <memory>

#include <quadcontrol_core/counter.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>
#include <std_srvs/srv/set_bool.hpp>

class Controller : public rclcpp::Node {
public:
  Controller()
  : Node("controller_node") {}

  void start()
  {
    publisher_ = create_publisher<std_msgs::msg::Int32>("/control_counter", 10);
    service_ = create_service<std_srvs::srv::SetBool>(
        "/reset_counter",
      [this](const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
      std::shared_ptr<std_srvs::srv::SetBool::Response> response) {
        handle_reset(request, response);
        });
    timer_ = create_wall_timer(std::chrono::milliseconds(100),
        [this]() {publish_counter();});

    RCLCPP_INFO(get_logger(), "Controller started");
  }

private:
  void handle_reset(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
    const std::shared_ptr<std_srvs::srv::SetBool::Response> response)
  {
    counter_.set_reset_requested(request->data);
    response->success = request->data;
    response->message =
      request->data ? "Counter reset requested" : "Counter request was false";
  }

  void publish_counter()
  {
    std_msgs::msg::Int32 message;
    message.data = counter_.next_value();
    RCLCPP_INFO(get_logger(), "Control loop %d", message.data);
    publisher_->publish(message);
  }

  Counter counter_;
  rclcpp::Publisher<std_msgs::msg::Int32>::SharedPtr publisher_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr service_;
  rclcpp::TimerBase::SharedPtr timer_;
};

auto main(int argc, char *argv[]) -> int
{
  rclcpp::init(argc, argv);

  auto controller = std::make_shared<Controller>();
  controller->start();
  rclcpp::spin(controller);

  rclcpp::shutdown();
  return 0;
}
