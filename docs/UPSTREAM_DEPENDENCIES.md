# Upstream simulation dependency — provenance and licensing

This project was developed and tested inside a Gazebo + MoveIt 2 simulation
environment provided for the course. That environment is a **separate third-party
repository**, not part of this project. This document records exactly which
upstream components this project needs, where each came from, and — importantly —
**why the environment is not bundled here.**

---

## The upstream repository

```
Repository : https://github.com/PieroSimonet/ir_2526
Commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Date       : 2025-09-10 16:23:42 +0200
Author     : pierosimonet <simonetto.piero@gmail.com>
Branch     : main (the only branch)
```

A full local snapshot of that commit (209 files) was taken during preparation and
its per-file SHA-256 manifest recorded, so the exact environment this project ran
against is preserved even if the upstream repository disappears.

## Why the environment is not bundled in this repository

**The upstream repository has no licence.** GitHub reports `license: null`, there
is no `LICENSE` file at its root, and three of its five packages declare
`<license>TODO: License declaration</license>` in their `package.xml`. Under
default copyright, that means **all rights reserved** — the code may be read and
used, but not redistributed.

There is also a specific course instruction not to commit the instructor's code as
part of the coursework, which points the same way.

So the environment is **deliberately not vendored here.** Copying it would be a
licence violation, and the honest position is to document the dependency rather
than quietly absorb it.

## Component-by-component licence matrix

Licence status was determined from each file's *own* copyright header, from
package-level `package.xml` declarations, and from whether the package actually
ships the licence text it declares.

### Needed by this project — UR5 manipulation

| Component | Upstream path | Licence | Bundled here? |
|---|---|---|---|
| Simulation launch | `ir_launch/launch/assignment_2.launch.py` | **BSD-3-Clause** (© 2022 Stogl Robotics Consulting UG) | No — see below |
| Robot bringup | `ir_movit_config/launch/ir_base.launch.py` | **BSD-3-Clause** (© 2021 Stogl Robotics) | No |
| MoveIt launch | `ir_movit_config/launch/ir_movit.launch.py` | **BSD-3-Clause** | No |
| Package manifest | `ir_movit_config/package.xml` | **BSD-3-Clause** (declared) | No |
| Controller config | `ir_movit_config/config/ros2_controllers.yaml` | **NO LICENCE** | No |
| MoveIt controller config | `ir_movit_config/config/moveit_controllers.yaml` | **NO LICENCE** | No |
| Kinematics / joint limits | `ir_movit_config/config/{kinematics,joint_limits}.yaml` | **NO LICENCE** | No |
| Semantic robot description | `ir_movit_config/config/ur_gripper.srdf` | **NO LICENCE** | No |
| URDF / xacro (gripper + environment) | `ir_movit_config/config/*.xacro` | **NO LICENCE** | No |
| Robot description (UR5 + Robotiq) | `ir_desription/urdf/**` (16 files) | **NO LICENCE** | No |
| Robot meshes | `ir_desription/meshes/ur5/**` (14 files) | **NO LICENCE** (derived from `ur_description`) | No |
| Robot config (kinematics, limits) | `ir_desription/config/**` (5 files) | **NO LICENCE** | No |
| Gazebo world (UR scene) | `ir_base/worlds/iaslab_ur.sdf*` | **NO LICENCE** | No |
| ROS–Gazebo bridge config | `ir_base/params/ur_bridge.yaml` | **NO LICENCE** | No |

> Note on the upstream package name: `ir_desription` is spelled that way upstream
> (a typo for "description"). It is reproduced here only where quoting the
> upstream layout; **changing it would break the launch files.**

### Summary

|  | Files | Redistributable? |
|---|---|---|
| BSD-3-Clause | 4 of the needed source files | **Yes, with attribution** |
| **No licence at all** | **46 source files + 14 mesh assets** (MoveIt configs, SRDF, URDF/xacro, meshes, world, bridge config) | **No** |

The permissive files are the *launch glue*. The MoveIt configuration, the robot
description, the meshes and the Gazebo world — everything that constitutes the
simulation — is unlicensed.

## Why a partial bundle was rejected

It would be lawful to copy only the BSD-3-Clause launch files. It was deliberately
**not done**, for three reasons:

1. **It would not make the project runnable.** `assignment_2.launch.py` immediately
   resolves `FindPackageShare("ir_movit_config")` and
   `FindPackageShare("ir_desription")`; with those absent it fails at once.
2. **It would misrepresent the state.** A `third_party/` directory holding a
   fragment implies self-containment that does not exist.
3. **It would degrade the repository.** A handful of launch files referencing
   absent packages is worse than a clear, documented dependency.

The lawful subset is staged locally and can be added in one commit the moment
permission is granted.

## What would make this project fully self-contained

### Option A — written permission from the author

The set that would achieve full self-containment:

```
ir_launch/launch/assignment_2.launch.py         BSD-3-Clause  - already permitted
ir_movit_config/launch/ir_base.launch.py        BSD-3-Clause  - already permitted
ir_movit_config/launch/ir_movit.launch.py       BSD-3-Clause  - already permitted
ir_movit_config/package.xml                     BSD-3-Clause  - already permitted
ir_movit_config/config/**                       needs permission   (14 files)
ir_desription/urdf/**                           needs permission   (16 files)
ir_desription/meshes/ur5/**                     needs permission   (14 files)
ir_desription/config/**                         needs permission   (5 files)
ir_base/worlds/iaslab_ur.sdf*                   needs permission
ir_base/params/ur_bridge.yaml                   needs permission
```

A short request to the author covering redistribution of the `ir_movit_config`
and `ir_desription` content under a permissive licence, with attribution, is all
that is required.

Attribution is not negotiable in return: the upstream author and the original
upstream projects (Universal Robots/`ur_description`, Robotiq, PickNik/MoveIt,
Stogl Robotics) would all be credited in a `NOTICE` file, and the modifications
made for the course would be stated, as BSD-3-Clause and Apache-2.0 §4(b) require.

### Option B — no permission available

Rebuild the description and configuration from permissively licensed upstream
projects instead of using the course's copies:

| Need | Legitimate upstream source |
|---|---|
| UR5 description + meshes | `ur_description` (BSD-3-Clause, Universal Robots) — the source of the meshes in `ir_desription` |
| Robotiq gripper description | `robotiq_description` (BSD-3-Clause, PickNik) |
| MoveIt configuration | `moveit_config` generated by MoveIt Setup Assistant (BSD-3-Clause, PickNik) |
| ros2_control config | `ur_robot_driver` examples (BSD-3-Clause) |
| World | would have to be re-authored — the course world is the author's own work |
| `ir_arm` planning group name | `manipulation_node.cpp` hard-codes it; a regenerated config must use the same name or the code must change |

This yields a runnable project owing nothing to the course repository, but the
scene layout and gripper geometry would differ, and the recorded demonstration
would no longer correspond exactly to the published configuration. That trade-off
is the user's to make, not one to make silently.

## Running it today, with the dependency

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/PieroSimonet/ir_2526.git
cd ir_2526 && git checkout d19ae7613e50112f9bcd8bd995bb4572ef71b821
# then clone this repository alongside it and build the workspace
cd ~/ros2_ws && colcon build --symlink-install
```

Pinning the commit matters: the upstream repository may change or disappear, and
this project was verified against `d19ae761`.

## Attribution

The simulation environment, the UR5 and Robotiq description, the MoveIt
configuration, the Gazebo world and the bridge configuration are the work of its
original author (**Piero Simonetto**, University of Padova). Nothing in this
repository claims that work. Where the environment is used, it is used unmodified
and credited.

The upstream launch files are themselves derived from:

- **Stogl Robotics Consulting UG (haftungsbeschränkt)** — BSD-3-Clause,
  author of the Universal Robots ROS 2 bringup launch files
- **PickNik, Inc.** — BSD-3-Clause
- **Universal Robots** — BSD-3-Clause (`ur_description`)
