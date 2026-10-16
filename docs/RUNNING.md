# Running this pipeline

The simulation environment is **vendored** in this repository under
[`third_party/ir_2526/`](../third_party/ir_2526/) — `ir_launch`, `ir_base`,
`ir_desription` and `ir_movit_config`. Nothing external needs to be cloned.

This document is the **interface reference**: exactly which topics, actions and
frames the nodes depend on, and what the environment must therefore provide. It is
useful if you want to run the pipeline against a different scene, or to understand
what the vendored environment is doing.

> **Provenance and licensing are in
> [`UPSTREAM_DEPENDENCIES.md`](UPSTREAM_DEPENDENCIES.md)** — the upstream
> repository and commit, the permission under which the environment is
> redistributed, and the attribution obligations.

---

## What the launch file calls

```python
prof_pkg_share = get_package_share_directory("ir_launch")
prof_launch_path = os.path.join(prof_pkg_share, "launch", "assignment_2.launch.py")

IncludeLaunchDescription(
    PythonLaunchDescriptionSource(prof_launch_path),
    launch_arguments={"use_sim_time": "true"}.items(),
)
```

So it requires:

- a package named `ir_launch` on the `AMENT_PREFIX_PATH`,
- a file `ir_launch/launch/assignment_2.launch.py`,
- that launch accepts a `use_sim_time` argument.

`assignment2.launch.py` then starts the four nodes of this package itself, with
`use_sim_time: true`, and delays `manipulation_node` by 2 seconds using
`TimerAction(period=2.0, ...)` so that perception is publishing before the
planner starts.

## Interfaces `ir_launch` must supply

Derived from the nodes' subscriptions, action clients and frame assumptions.

### Simulation

| Requirement | Why |
|---|---|
| A UR5 arm in Gazebo, planning group named **`ir_arm`** | `manipulation_node.cpp` hard-codes `PLANNING_GROUP = "ir_arm"` |
| A Robotiq 85 gripper | the TF tree captured at runtime contains `robotiq_85_right_knuckle_link` and the rest of the gripper chain |
| A gripper action server at `/gripper_controller/gripper_cmd`, type `control_msgs/action/GripperCommand` | the node waits 5 s for this server at startup and exits with an error if it is missing |
| An RGB camera publishing `sensor_msgs/Image` on `/rgb_camera/image` and `sensor_msgs/CameraInfo` on `/rgb_camera/camera_info` | `tag_detector_node.py` needs the intrinsics (`fx, fy, cx, cy`) for PnP pose estimation |
| `use_sim_time: true` throughout | all four nodes are launched with it; the fusion node compares message stamps against the node clock |

### Transforms

| Requirement | Why |
|---|---|
| a chain from the camera frame to `base_link` at the image timestamp | `tag_detector_node.py` transforms each tag detection into `base_link` |
| a frame named `tool0` on the arm's end effector | the `OrientationConstraint` is attached to `tool0` |

The captured transform tree in `docs/figures/tf_tree_ur5_run.png` shows the
frames that were live during a real run, and is the best available reference for
what the environment provided.

---

## Reconstruction with standard upstream packages

**This has not been tested.** No ROS 2 or MoveIt 2 installation was available
during preparation, so the following is a documented starting point, not a
verified procedure.

The upstream packages that would satisfy the requirements above:

- a UR5 description package (`ur_description` / `ur_moveit_config`, or the
  course's own URDF)
- `moveit_config` / `moveit2` for the planning pipeline, with a planning group
  that must be **named `ir_arm`** or the C++ node will not find it
- `robotiq` gripper description plus a `ros2_control` gripper controller exposing
  the `GripperCommand` action at `/gripper_controller/gripper_cmd`
- `gazebo_ros` for the simulation
- an RGB camera sensor publishing on `/rgb_camera/image` with matching
  `camera_info`

**Caveats to expect:**

- the planning group name `ir_arm` is hard-coded in `manipulation_node.cpp`; a
  standard `ur_moveit_config` names its group differently, so either the config or
  the code must change;
- the manipulation sequence encodes absolute positions, the buffer location and
  cube dimensions for the course's specific scene — see the README's *Known
  limitations*. Reproducing the environment does **not** guarantee the sequence
  succeeds in a differently-laid-out scene;
- the camera topic names `/rgb_camera/*` are specific to the provided world.

---

## What we could not verify

| Item | Status |
|---|---|
| `ir_launch` contents | not available — not in the original repository, and not provided |
| The URDF / MoveIt config for the arm | not in the original repository |
| ROS 2 distribution | not declared anywhere |
| Whether the reconstruction above works | untested |
| Whether the sequence succeeds in a rebuilt scene | unknown |
