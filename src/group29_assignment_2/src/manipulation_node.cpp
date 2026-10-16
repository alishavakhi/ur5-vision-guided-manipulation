#include <rclcpp/rclcpp.hpp>
#include <rclcpp/node_options.hpp>
#include <memory>
#include <thread>
#include <chrono>
#include <future>
#include <mutex>
#include <optional>


// MoveIt Headers
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <moveit/robot_state/robot_state.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <moveit/planning_scene_interface/planning_scene_interface.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <control_msgs/action/gripper_command.hpp>

using GripperCommand = control_msgs::action::GripperCommand;
using GoalHandleGripper = rclcpp_action::ClientGoalHandle<GripperCommand>;


int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);

    rclcpp::NodeOptions node_options;
    node_options.automatically_declare_parameters_from_overrides(true);


    auto node = rclcpp::Node::make_shared("manipulation_node", node_options);
    const auto& LOGGER = node->get_logger();

    std::mutex pose_mtx;
    std::optional<geometry_msgs::msg::PoseStamped> sub_locA;
    std::optional<geometry_msgs::msg::PoseStamped> sub_locB;


    auto gripper_client = rclcpp_action::create_client<GripperCommand>(
        node, "/gripper_controller/gripper_cmd");

    std::thread([&node]() { rclcpp::spin(node); }).detach();

    std::this_thread::sleep_for(std::chrono::seconds(2));

    if (!gripper_client->wait_for_action_server(std::chrono::seconds(5))) {
        RCLCPP_ERROR(LOGGER, "Gripper action server not available");
        rclcpp::shutdown();
        return 1;
    }

    auto gripper_send = [&](double position, double max_effort) -> bool {
        GripperCommand::Goal goal;
        goal.command.position = position;
        goal.command.max_effort = max_effort;

        auto goal_handle_future = gripper_client->async_send_goal(goal);

        if (goal_handle_future.wait_for(std::chrono::seconds(5)) != std::future_status::ready) {
            RCLCPP_ERROR(LOGGER, "Timeout waiting for gripper goal handle");
            return false;
        }

        auto goal_handle = goal_handle_future.get();
        if (!goal_handle) {
            RCLCPP_ERROR(LOGGER, "Gripper goal rejected");
            return false;
        }

        auto result_future = gripper_client->async_get_result(goal_handle);

        if (result_future.wait_for(std::chrono::seconds(10)) != std::future_status::ready) {
            RCLCPP_ERROR(LOGGER, "Timeout waiting for gripper result");
            return false;
        }

        auto result = result_future.get();
        return result.code == rclcpp_action::ResultCode::SUCCEEDED;
    };

        auto subA = node->create_subscription<geometry_msgs::msg::PoseStamped>(
        "/cube_a_pose", 10,
        [&](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        {
        std::lock_guard<std::mutex> lk(pose_mtx);
        sub_locA = *msg;
        }
       
        });

        auto subB = node->create_subscription<geometry_msgs::msg::PoseStamped>(
        "/cube_b_pose", 10,
        [&](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        {
        std::lock_guard<std::mutex> lk(pose_mtx);
         sub_locB = *msg;
        }
       
    });


    auto open_gripper = [&]() { return gripper_send(0.00, 20.0); };
    auto close_gripper = [&]() { return gripper_send(0.2, 20.0); };



    static const std::string FRAME_ID = "base_link";
    static const std::string PLANNING_GROUP = "ir_arm";

    moveit::planning_interface::MoveGroupInterface move_group(node, PLANNING_GROUP);
    moveit::planning_interface::MoveGroupInterface::Plan my_plan;

    move_group.setMaxVelocityScalingFactor(1.0);
    move_group.setMaxAccelerationScalingFactor(1.0);
    move_group.setPlanningTime(5.0);

    auto move = [&](const geometry_msgs::msg::PoseStamped& target) -> bool {
    geometry_msgs::msg::PoseStamped vertical_pose = move_group.getCurrentPose();

    moveit_msgs::msg::OrientationConstraint ocm;
    ocm.link_name = "tool0";
    ocm.header.frame_id = FRAME_ID;
    ocm.orientation = vertical_pose.pose.orientation;
    ocm.absolute_x_axis_tolerance = 0.9;
    ocm.absolute_y_axis_tolerance = 0.9;
    ocm.absolute_z_axis_tolerance = 3.14;
    ocm.weight = 1.0;

    moveit_msgs::msg::Constraints constraints;
    constraints.orientation_constraints.push_back(ocm);
    move_group.setPathConstraints(constraints);

    move_group.setPoseTarget(target);

    bool ok = false;
    if (move_group.plan(my_plan) == moveit::core::MoveItErrorCode::SUCCESS) {
        move_group.execute(my_plan);
        ok = true;
    } else {
        RCLCPP_ERROR(LOGGER, "MOVE failed");
        ok = false;
        }

    move_group.clearPathConstraints();
    return ok;
    };

    auto approach = [&](const geometry_msgs::msg::PoseStamped& target, double dz) -> bool {
    geometry_msgs::msg::PoseStamped p = target;
    p.pose.position.z += dz;
    return move(p);
    };

    auto depart = [&](const geometry_msgs::msg::PoseStamped& target, double dz) -> bool {
    geometry_msgs::msg::PoseStamped p = target;
    p.pose.position.z += dz;
    return move(p);
    };




    geometry_msgs::msg::PoseStamped p = move_group.getCurrentPose();
    RCLCPP_INFO(LOGGER, "Current Pose frame id: %s", p.header.frame_id.c_str());


   
    
    rclcpp::Rate rate(30);
    RCLCPP_INFO(LOGGER, "Waiting for /cube_a_pose and /cube_b_pose ...");

    while (rclcpp::ok()) {
    bool ready = false;
    {
    std::lock_guard<std::mutex> lk(pose_mtx);
    ready = sub_locA.has_value() && sub_locB.has_value();
    }
    if (ready) break;
    rate.sleep();
     }

    RCLCPP_INFO(LOGGER, "Both locA and locB are available now.");

    geometry_msgs::msg::PoseStamped msgA, msgB;
    {
        std::lock_guard<std::mutex> lk(pose_mtx);
        msgA = *sub_locA;
        msgB = *sub_locB;
    }
    
     
    moveit::planning_interface::PlanningSceneInterface planning_scene_interface;

// ---------- BOX 1 ----------
moveit_msgs::msg::CollisionObject box1;
box1.header.frame_id = FRAME_ID;
box1.id = "box1";

shape_msgs::msg::SolidPrimitive primitive1;
primitive1.type = primitive1.BOX;
primitive1.dimensions = {0.06, 0.06, 0.1};

geometry_msgs::msg::Pose pose1;
pose1.orientation.w = 1.0;
pose1.position.x = msgA.pose.position.x+0.03;
pose1.position.y = msgA.pose.position.y;
pose1.position.z = msgA.pose.position.z-0.065;

box1.primitives.push_back(primitive1);
box1.primitive_poses.push_back(pose1);
box1.operation = box1.ADD;


// ---------- BOX 2 ----------
moveit_msgs::msg::CollisionObject box2;
box2.header.frame_id = FRAME_ID;
box2.id = "box2";

shape_msgs::msg::SolidPrimitive primitive2;
primitive2.type = primitive2.BOX;
primitive2.dimensions = {0.06, 0.06, 0.1};

geometry_msgs::msg::Pose pose2;
pose2.orientation.w = 1.0;
pose2.position.x = msgB.pose.position.x+0.03;
pose2.position.y = msgB.pose.position.y;
pose2.position.z = msgB.pose.position.z-0.06;

box2.primitives.push_back(primitive2);
box2.primitive_poses.push_back(pose2);
box2.operation = box2.ADD;

// ---------- BOX 3 ----------
moveit_msgs::msg::CollisionObject box3;
box3.header.frame_id = FRAME_ID;
box3.id = "box3";

shape_msgs::msg::SolidPrimitive primitive3;
primitive3.type = primitive3.BOX;
primitive3.dimensions = {0.06, 0.06, 0.1};
geometry_msgs::msg::Pose pose3;
pose3.orientation.w = 1.0;
pose3.position.x = msgA.pose.position.x-0.07;
pose3.position.y = msgA.pose.position.y+0.1;
pose3.position.z = msgA.pose.position.z-0.065;

box3.primitives.push_back(primitive3);
box3.primitive_poses.push_back(pose3);
box3.operation = box3.ADD;


planning_scene_interface.applyCollisionObjects({box1, box2});


    std::vector<double> joint_values = {1.57, -1.499, 0.677, -0.809, -1.633, 0.080}; // radians

    move_group.setJointValueTarget(joint_values);

    if (move_group.plan(my_plan) == moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_INFO(LOGGER, "Planning to locH pose SUCCESSFUL. Executing...");
        move_group.execute(my_plan);
    } else {
        RCLCPP_ERROR(LOGGER, "Planning to locH pose FAILED (GOAL_STATE_INVALID likely). This confirms your current pose is illegal in the planning scene.");
    }
    
    geometry_msgs::msg::PoseStamped Waypoint = move_group.getCurrentPose();
 
    Waypoint.pose.position.x = 0.3;
    Waypoint.pose.position.z = 0.5;
    Waypoint.header.frame_id = FRAME_ID; 
    Waypoint.pose.orientation.w = 0.0;
    Waypoint.pose.orientation.x = 1.0;
    Waypoint.pose.orientation.y = 0.0;
    Waypoint.pose.orientation.z = 0.0;

    move_group.setPoseTarget(Waypoint);

    if (move_group.plan(my_plan) == moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_INFO(LOGGER, "Planning to current pose SUCCESSFUL. Executing...");
        move_group.execute(my_plan);
    } else {
        RCLCPP_ERROR(LOGGER, "Planning to current pose FAILED (GOAL_STATE_INVALID likely). This confirms your current pose is illegal in the planning scene.");
    }


    
    geometry_msgs::msg::PoseStamped loc_A = move_group.getCurrentPose();
    loc_A.pose.position.x = msgA.pose.position.x+0.03;
    loc_A.pose.position.y = msgA.pose.position.y;
    loc_A.pose.position.z = msgA.pose.position.z + 0.145;          
    loc_A.header.frame_id = FRAME_ID;    

    approach(loc_A, 0.035);   
    open_gripper();
    move(loc_A);             
    close_gripper();   
    depart(loc_A, 0.035);  
    planning_scene_interface.removeCollisionObjects({"box1"});    

    geometry_msgs::msg::PoseStamped loc_Safe = move_group.getCurrentPose();
    
    loc_Safe.pose.position.x = msgA.pose.position.x-0.07;
    loc_Safe.pose.position.y = msgA.pose.position.y+0.1;
    loc_Safe.pose.position.z = msgA.pose.position.z + 0.15; 
    loc_Safe.header.frame_id = FRAME_ID; 

    approach(loc_Safe, 0.035);   
    move(loc_Safe);
    open_gripper();             
    depart(loc_Safe, 0.035);
    planning_scene_interface.applyCollisionObjects({box3}); 
    
    geometry_msgs::msg::PoseStamped Waypoint2 = move_group.getCurrentPose();
    
    Waypoint2.pose.position.x = 0.3;
    Waypoint2.pose.position.z -= 0.0;
    Waypoint2.pose.position.y = -0.2;
    Waypoint2.header.frame_id = FRAME_ID; 

    move(Waypoint2);

     geometry_msgs::msg::PoseStamped loc_B = move_group.getCurrentPose();
    
    loc_B.pose.position.x = msgB.pose.position.x+0.03;
    loc_B.pose.position.y = msgB.pose.position.y;
    loc_B.pose.position.z = msgB.pose.position.z + 0.15;
    loc_B.header.frame_id = FRAME_ID; 

    approach(loc_B, 0.035);   
    move(loc_B);             
    close_gripper();   
    depart(loc_B, 0.045); 
    planning_scene_interface.removeCollisionObjects({"box2"});

    approach(loc_A, 0.035);   
    move(loc_A); 
    open_gripper();           
    depart(loc_A, 0.035); 
    planning_scene_interface.applyCollisionObjects({box1});

    approach(loc_Safe, 0.035);   
    move(loc_Safe); 
    close_gripper();               
    depart(loc_Safe, 0.035); 
    planning_scene_interface.removeCollisionObjects({"box3"});
    move(Waypoint2);
    
    approach(loc_B, 0.035); 
    move(loc_B); 
    open_gripper();             
    depart(loc_B, 0.035); 
    planning_scene_interface.applyCollisionObjects({box2});

    move_group.setJointValueTarget(joint_values);

    if (move_group.plan(my_plan) == moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_INFO(LOGGER, "Planning to locH pose SUCCESSFUL. Executing...");
        move_group.execute(my_plan);
    } else {
        RCLCPP_ERROR(LOGGER, "Planning to locH pose FAILED (GOAL_STATE_INVALID likely). This confirms your current pose is illegal in the planning scene.");
    }

    
    gripper_send(1, 20.0);
    
    RCLCPP_INFO(LOGGER, "Process finished. Shutting down.");
    rclcpp::shutdown();
    return 0;
}