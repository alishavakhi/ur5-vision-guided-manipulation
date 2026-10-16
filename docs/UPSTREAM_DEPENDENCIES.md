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
  and licence status for every component, including the excluded ones
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
Included here       : 133 files, SHA-256 verified byte-identical
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

The permission is the author's to give for **his own work**. Two asset groups
inside the environment belong to other people and carry no licence of their own.
Neither is published here on the strength of the author's permission, and neither
is needed to build or run either project.

| Asset | Author | Status |
|---|---|---|
| `ir_base/models/artag/` (36 files) | **Nicola Castaman** | **Replaced.** The marker images are regenerated from the public BSD-2-Clause AprilTag `tag36h11` family definition. Same tag ids, same geometry, same paths — verified by decoding each marker with the reference detector |
| `ir_base/models/walls/arena_walls/` (3 files) | **Elisa Tosello** | **Excluded, not replaced.** Referenced by no world file, so nothing is affected |
| `ir_base/models/{build,install,log}/` (35 files) | — | Excluded: colcon build output committed upstream by accident, also embedding the upstream author's local path |

Components whose licences **do** permit redistribution and are included:
`apriltag_ros` (MIT, © 2017 Christian Rauch), `cafe_table` (CC-BY-3.0, © 2012
Nathan Koenig), the Robotiq gripper description (BSD-3-Clause, © 2022 PickNik
Robotics) and the UR5 meshes (BSD-3-Clause, Universal Robots).

> **This is not a byte-for-byte complete copy of the upstream repository, and is
> not described as one.** The full 207-file snapshot is preserved privately outside
> this repository with a per-file SHA-256 manifest, and the exact 74 excluded paths
> are enumerated in [`third_party/ir_2526/NOTICE`](../third_party/ir_2526/NOTICE)
> section 6.

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
