# ir_2526 — the simulation environment, preserved complete

This directory holds the simulation environment that both of this author's ROS 2
projects run in. It is included **in full** — every tracked file from the upstream
repository — so that neither project depends on an external GitHub repository
remaining available, being kept public, or staying unchanged.

```
Upstream repository : https://github.com/PieroSimonet/ir_2526
Upstream commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Commit date         : 2025-09-10 16:23:42 +0200
Commit author       : Piero Simonetto <simonetto.piero@gmail.com>
                     University of Padova
Upstream files      : 207 tracked files
Included here       : 207 — all of them
```

**Every file is byte-identical to that commit.** Nothing was renamed, reformatted,
reordered or edited. Verified by SHA-256 against the upstream snapshot after
copying: 205 files + 2 symlinks, 0 mismatches.

---

## What is here

| Package | Files | What it provides |
|---|---|---|
| `ir_base/` | 121 | the worlds, occupancy maps, Nav2 parameters, robot and camera descriptions, rviz config, and the `artag`, `cafe_table`, `objects`, `docks` and `walls` models |
| `ir_desription/` | 36 | the UR5 arm and Robotiq gripper description, meshes, and kinematics/physical configuration |
| `ir_movit_config/` | 30 | the MoveIt 2 configuration, controllers, SRDF, xacro and the controller spawner source |
| `apriltag_ros/` | 14 | the `apriltag_ros` node (v3.3.0, MIT) used by the TurtleBot 3 pipeline |
| `ir_launch/` | 6 | the simulation entry points, including `assignment_1.launch.py` and `assignment_2.launch.py` |

Package names and directory names are unchanged, including upstream's own
misspelling of `ir_desription`. The launch files and the Gazebo worlds resolve
packages by name — `get_package_share_directory('ir_base')`,
`model://ir_base/models/...` — so renaming anything would break the environment.

> `ir_launch` and `ir_movit_config` contain launch files for exercises beyond this
> author's two projects. They are included deliberately: this directory is a
> complete preservation, not a per-project subset. Several are alternatives for the
> same scenario.

### Generated files are included too

The 35 colcon artefacts under `ir_base/models/{build,install,log}/` are present,
byte-identical. They are build output rather than source — upstream committed them
by accident, under a `models/` directory that was itself treated as a colcon
workspace — but they are part of the upstream tree, so they are part of this
preservation. Upstream's `.gitignore`-style rules do not apply here: the
repository's own `.gitignore` carries a targeted exception for those three paths.

They also embed the upstream author's local filesystem path (`/home/piero`). That
is his own content, published in his own public repository, and it is reproduced
here unaltered along with everything else.

## Completely complete

There are **no exclusions.** Every one of the 207 tracked upstream files is
present, at its original path, with its original bytes:

| Group | Files | Status |
|---|---|---|
| All upstream source, models, worlds, meshes and configuration | 172 | included, byte-identical |
| colcon build output under `ir_base/models/{build,install,log}/` | 35 | included, byte-identical |
| **Total** | **207** | **included** |

`models/artag/` (Nicola Castaman) and `models/walls/arena_walls/` (Elisa Tosello)
are included with their authors' permission, confirmed by the repository owner.
Their original `model.config` credits — which name each author and their contact
address — are reproduced unmodified. See [`NOTICE`](NOTICE) section 3.

## Defects inherited from upstream

Three files in this directory are broken upstream, byte-identical to the commit
above, and kept that way. They are on no launch path, so neither project is
affected — they are recorded here so a future reader does not mistake them for
damage introduced during preparation.

| File | Defect |
|---|---|
| `ir_movit_config/launch/simulation_complete.launch.py` | Python `SyntaxError` — unterminated string literal at line 49. It could never have run as written |
| `ir_movit_config/launch/ir_ur.py` | references an `ir_arena` package that does not exist anywhere in the upstream repository, so it could never have run |
| `ir_desription/urdf/ur_gripper_base.urdf` | not a URDF: 41 bytes of captured terminal output, `[ros2run]: Process exited with failure 2` |

They are allow-listed by name in `tools/static_checks.py`, so that a genuine new
failure is never hidden behind a permanently red check.

## Integrity

| Check | Result |
|---|---|
| Files verified by SHA-256 against upstream | 207 / 207 |
| Content mismatches | 0 |
| Renames, reformats or edits | 0 |

The upstream snapshot, with a per-file SHA-256 manifest, is also held outside both
repositories:

```
snapshot : ~/engineering-portfolio/work/third_party_inspect/ir_2526/
manifest : ~/engineering-portfolio/manifests/ir_2526-FULL.sha256   (207 entries)
```

## Using it

The repository root is the colcon workspace, so `src/` and `third_party/` build in
a single pass:

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src third_party --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Standard ROS 2 packages must still be installed; the environment needs Nav2,
`turtlebot3`, `ros_gz`, MoveIt 2, `ur_description`, `robotiq_description` and
`apriltag_ros`. Both READMEs list the exact sets.

## Attribution

The simulation environment — its worlds, maps, robot and camera descriptions, UR5
and gripper models, MoveIt 2 configuration and Nav2 tuning — is the work of
**Piero Simonetto** (University of Padova), redistributed with his permission.
Nothing in this repository claims that work as its author's.

The ARTag model and marker images are the work of **Nicola Castaman**. The
`arena_walls` model is the work of **Elisa Tosello**. Both are included with their
authors' permission, with their own authorship notices preserved in their
`model.config` files.

`apriltag_ros` is the work of **Christian Rauch**, used under the MIT licence. The
cafe table model is by **Nathan Koenig**, CC-BY-3.0. The Robotiq gripper
description is by **PickNik Robotics**, BSD-3-Clause.

Full component-by-component status: [`NOTICE`](NOTICE).
