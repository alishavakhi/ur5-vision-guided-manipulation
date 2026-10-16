# Simulation environment — provenance, permission and licensing

The Gazebo simulation environment these projects run in was **written by someone
else**. It is preserved complete under
[`third_party/ir_2526/`](../third_party/ir_2526/).

This document is the short version: where it came from and what permission exists.
The authoritative component-by-component record — what is included, what is not,
and the licence status of each part — lives with the code:

- **[`third_party/ir_2526/README.md`](../third_party/ir_2526/README.md)** — what is
  in the tree, what is deliberately not, and the per-package breakdown
- **[`third_party/ir_2526/NOTICE`](../third_party/ir_2526/NOTICE)** — attribution
  and licence status for every component
- **[`third_party/ir_2526/licenses/`](../third_party/ir_2526/licenses/)** — the full
  text of every licence relied on

---

## Provenance

```
Upstream repository : https://github.com/PieroSimonet/ir_2526
Upstream commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Commit date         : 2025-09-10 16:23:42 +0200
Commit author       : Piero Simonetto <simonetto.piero@gmail.com>
                      University of Padova
Upstream files      : 207 tracked files
Included here       : 207 files - all of them, SHA-256 verified byte-identical
```

## Permission

The environment is redistributed **with the author's permission**, granted on the
basis that attribution is maintained.

The upstream repository carries **no licence**: GitHub reports `license: null`,
there is no `LICENSE` file at its root, and the packages declare
`<license>TODO: License declaration</license>`. No licence is therefore asserted
for this material, and none was invented. Its stated status is:

> Redistributed with the author's permission. Copyright remains with the original
> authors. All rights reserved other than the redistribution expressly permitted
> here.

The vendored files are **not** covered by this repository's Apache-2.0 licence,
which applies only to `src/`, `docs/` and the READMEs.

## Scope — what that permission does and does not reach

## Scope — complete, including two assets held under separate permission

**All 207 tracked upstream files are included. Nothing is excluded.**

Most of the environment is the author's own work, redistributed under his
permission. Two asset groups inside it belong to other people, carry no licence of
their own, and are included **with their authors' permission**, their own credit
blocks reproduced unmodified.

| Asset | Author | Status |
|---|---|---|
| `ir_base/models/artag/` (36 files) | **Nicola Castaman** | Included with the author's permission. The 18 marker images render the AprilTag `tag36h11` family, whose definition is BSD-2-Clause |
| `ir_base/models/walls/arena_walls/` (3 files) | **Elisa Tosello** | Included with the author's permission. "Unipd Autonomous Robotics Arena Walls" |
| `ir_base/models/{build,install,log}/` (35 files) | — | Included. Generated colcon output — the environment author's own, covered by the same permission |

Components with their own licences, also included: `apriltag_ros` (MIT, © 2017
Christian Rauch), `cafe_table` (CC-BY-3.0, © 2012 Nathan Koenig), the Robotiq
gripper description (BSD-3-Clause, © 2022 PickNik Robotics) and the UR5 meshes
(BSD-3-Clause, Universal Robots).

> **This is a byte-for-byte complete copy of the upstream repository at
> `d19ae761`.** All 207 files are present at their original paths, SHA-256 verified
> against the upstream commit: 0 mismatches. The same snapshot is preserved
> privately with a per-file manifest.

## Still required from the system

Ordinary ROS 2 distribution packages, installed through `rosdep`/`apt`: Nav2,
`turtlebot3`, `ros_gz`, `apriltag_ros`, `image_proc`, MoveIt 2,
`ur_description`, `robotiq_description`, `xacro`. Each is under its own licence
and none is vendored. See the README's install section, or
[`TEST_PLAN.md`](TEST_PLAN.md) for the exact sets.

## ROS 2 distribution

**Jazzy**, inferred from 18 mesh paths hard-coded as
`file:///opt/ros/jazzy/share/robotiq_description/...` inside the vendored
`ur_gripper.urdf`, which is byte-identical to upstream. Since those paths are
absolute, the UR5 project requires Jazzy; on any other distribution the gripper
meshes will not resolve without a symlink or a patch. See
[`TEST_PLAN.md`](TEST_PLAN.md) section 0.

## Attribution

The simulation environment — its worlds, maps, robot and camera descriptions, UR5
and Robotiq models, MoveIt 2 configuration and Nav2 tuning — is the work of
**Piero Simonetto** (University of Padova), used unmodified and not claimed as this
project's author's work.
