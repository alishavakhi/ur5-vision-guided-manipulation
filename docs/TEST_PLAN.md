# Test plan and reproducibility procedure

How to build, launch and verify this repository, and what can be automated.

Nothing in this plan has been executed on the preparation host — there is no ROS 2
installation there. Every expected output below was derived by reading the source,
and is labelled as derived rather than observed.

---

## 0. The ROS 2 distribution: Jazzy

The original project never declared a distribution. There is nevertheless direct
evidence for one:

```
third_party/ir_2526/ir_desription/urdf/ur_gripper.urdf

18 mesh paths written as:
  <mesh filename="file:///opt/ros/jazzy/share/robotiq_description/meshes/visual/robotiq_base.dae"/>
```

That file is byte-identical to upstream `d19ae761`, so the hard-coded
`/opt/ros/jazzy` is the environment author's own, not an artefact of preparation.

| Finding | Consequence |
|---|---|
| The vendored UR5 gripper URDF hard-codes `/opt/ros/jazzy/...` in 18 places | The environment this project ran in was **ROS 2 Jazzy** |
| Those paths are absolute | On Humble or anything else the gripper meshes will not resolve without a symlink or a patch |

This is inference from an artefact, not a declaration. **Target ROS 2 Jazzy on
Ubuntu 24.04.** Confirm with whoever ran the original experiments before treating
it as certain.

---

## 1. Environment

```
Ubuntu 24.04 (Noble) + ROS 2 Jazzy (ros-jazzy-desktop) + Gazebo Sim (via ros_gz)
colcon, rosdep, python3-colcon-common-extensions
```

Install the dependencies listed in the README's
[Installation](../README.md#installation-and-build) section, then:

## 2. Build

```bash
git clone https://github.com/alishavakhi/ur5-vision-guided-manipulation.git ~/ros2_ws
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src third_party --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

The repository root **is** the colcon workspace, so `src/` and `third_party/` are
discovered in one pass.

| Expected | Value |
|---|---|
| Packages built | see the README's build section |
| Success looks like | `Summary: N packages finished` with the expected N |
| Failure to watch for | the single compiled C++ target, if this repository has one |

## 3. Launch and expected outputs

The exact launch commands and the expected nodes, topics, actions, controllers and
TF frames are listed in the README's [Running the system](../README.md#running-the-system)
section — they are not duplicated here. Verify them with:

```bash
ros2 node list
ros2 topic list
ros2 topic hz <topic>
ros2 run tf2_tools view_frames     # writes frames.pdf
ros2 action list
```

Known third-party defect to expect during a file-by-file review:
`ir_desription/urdf/ur_gripper_base.urdf` is 41 bytes of captured terminal output
(`[ros2run]: Process exited with failure 2`), committed upstream by accident. It is
on no launch path and is harmless.

## 4. Automation layers

| Layer | Needs | What it catches | Automate |
|---|---|---|---|
| **0 — static** | nothing | syntax errors, malformed manifests, unresolvable package references, undeclared executables, dead doc links and anchors, secrets, missing licence/attribution files, missing README sections | every commit |
| **1 — build** | ROS 2 Jazzy | compile and link failures | every push |
| **2 — headless launch** | Gazebo, no GUI | missing nodes, topics or TF frames at run time | nightly |
| **3 — functional** | full stack | behaviour — detection, filtering, control, planning | release |

Layer 0 is implemented and runnable now:

```bash
python3 tools/static_checks.py
```

It needs no ROS installation, exits non-zero on failure, and is suitable as a
pre-commit hook or a CI step. Layers 1–3 have not been run anywhere in this
project's preparation.

### Functional tests that are worth writing (layer 3)

| Test | Method | Notes |
|---|---|---|
| AprilTag detection | publish the regenerated markers as a synthetic camera image, assert the tag id comes back | deterministic, no physics |
| Kalman estimator | feed a noisy pose sequence, assert convergence and that the estimate is smoother than the raw midpoint | runs as a unit test |
| Colour classification | feed fixed frames, assert the colour name and confidence | pure function |
| Corridor controller | replay a recorded LiDAR scan, assert entry/exit and control output | needs the recorded scan |
| MoveIt planning | plan to a known pose, assert a plan is returned | needs the description loaded |
| End-to-end sequence | run the action, assert success | slowest and most fragile — manual, at release |

## 5. Rules for using this plan

- Do not modify the algorithms to make a test pass.
- Do not report a layer as passing unless it was executed. Layers 1–3 have not
  been run.
- The layer-0 suite proves the tree is well-formed, not that the system runs. Those
  are different sentences and must stay different.
