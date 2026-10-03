#include <chrono>
#include <memory>

#include <quadcontrol_core/counter.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>
#include <std_srvs/srv/set_bool.hpp>

/**
 * @brief ROS 2 node responsible for the quadrotor control loop.
 *
 * The Controller publishes the control counter periodically and provides
 * a ROS 2 service that allows the counter to be reset.
 */
class Controller : public rclcpp::Node {
public:
  /**
   * @brief Constructs the controller node.
   *
   * Creates a ROS 2 node named "controller_node".
   */
  Controller()
  : Node("controller_node") {}

  /**
   * @brief Initializes the controller's ROS 2 interfaces.
   *
   * Creates the counter publisher, reset service, and periodic control-loop
   * timer.
   */
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
  /**
   * @brief Handles requests to reset the control counter.
   *
   * Updates the counter reset state according to the service request and
   * populates the corresponding service response.
   *
   * @param request Service request containing the reset command.
   * @param response Service response reporting whether the request was accepted.
   */
  void handle_reset(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
    const std::shared_ptr<std_srvs::srv::SetBool::Response> response)
  {
    counter_.set_reset_requested(request->data);
    response->success = request->data;
    response->message =
      request->data ? "Counter reset requested" : "Counter request was false";
  }

  /**
   * @brief Executes one iteration of the control loop.
   *
   * Retrieves the next counter value, publishes it on the control counter
   * topic, and logs the current value.
   */
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

/**
 * @brief Application entry point.
 *
 * Initializes ROS 2, creates and starts the Controller node, and enters
 * the ROS 2 event loop.
 *
 * @param argc Number of command-line arguments.
 * @param argv Command-line arguments.
 * @return Zero on successful shutdown.
 */
auto main(int argc, char *argv[]) -> int
{
  rclcpp::init(argc, argv);

  auto controller = std::make_shared<Controller>();
  controller->start();
  rclcpp::spin(controller);

  rclcpp::shutdown();
  return 0;
}