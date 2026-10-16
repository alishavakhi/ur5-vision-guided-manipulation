#include <chrono>
#include <memory>
#include <vector>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

using namespace std::chrono_literals;

class ShortJointStatePublisher : public rclcpp::Node
{
public:
    ShortJointStatePublisher()
    : Node("short_joint_state_publisher")
    {
        publisher_ = this->create_publisher<sensor_msgs::msg::JointState>("joint_states", 10);

        // Create joint_state message
        msg_.header.frame_id = "";
        msg_.name = {"elbow_joint",
                     "robotiq_85_left_knuckle_joint",
                     "shoulder_lift_joint",
                     "shoulder_pan_joint",
                     "wrist_1_joint",
                     "wrist_2_joint",
                     "wrist_3_joint"};
        msg_.position = {-0.0028067519888281822,
                          0.7666177749633789,
                          -1.5699265003204346,
                          3.6449958429329854e-07,
                          -1.5689884424209595,
                          -1.402064413014159e-06,
                          0.0012554670684039593};
        msg_.velocity = {-1.0977964848279953e-07,
                         -1.3338139979168773e-06,
                         5.319493357092142e-05,
                         0.0,
                         5.364418029785156e-05,
                         5.820766091346741e-11,
                         -5.4424162954092026e-08};
        msg_.effort = {0.011702235783791998,
                       0.04587634249310213,
                       -0.013371340934505895,
                       -5.628243684441259e-07,
                       0.0004113466711714864,
                       -0.00021411395573522896,
                       -0.00017658483774596334};

        // Publish repeatedly for 2 seconds
        timer_ = this->create_wall_timer(
            100ms, std::bind(&ShortJointStatePublisher::publish_once, this));

        start_time_ = this->now();
    }

private:
    void publish_once()
    {
        auto elapsed = this->now() - start_time_;
        if (elapsed.seconds() < 5.0) {
            msg_.header.stamp = this->get_clock()->now();
            publisher_->publish(msg_);
        } else {
            RCLCPP_INFO(this->get_logger(), "Published joint state for 2 seconds, shutting down.");
            rclcpp::shutdown();
        }
    }

    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr publisher_;
    sensor_msgs::msg::JointState msg_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Time start_time_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ShortJointStatePublisher>());
    rclcpp::shutdown();
    return 0;
}

