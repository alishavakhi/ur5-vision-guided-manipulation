# ir_2526 — the simulation environment, preserved complete

This directory holds the simulation environment that both of this author's ROS 2
projects run in. It is included **in full** so that neither repository depends on
an external GitHub repository remaining available, being kept public, or staying
unchanged.

```
Upstream repository : https://github.com/PieroSimonet/ir_2526
Upstream commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Commit date         : 2025-09-10 16:23:42 +0200
Commit author       : Piero Simonetto <simonetto.piero@gmail.com>
                     University of Padova
Upstream files      : 207 tracked files
Included here       : 168 files
```

The environment is redistributed **with the author's permission**, on the basis
that attribution is maintained. It is not licensed to this project, and no licence
was invented for it — see [`NOTICE`](NOTICE) for the exact status of every
component, and [`licenses/`](licenses/) for the licence texts that do apply.

---

## What is here

Every file is byte-identical to the upstream commit above. Nothing was renamed,
reformatted, reordered or edited.

| Package | Files | What it provides |
|---|---|---|
| `ir_base/` | 82 | the worlds, occupancy maps, Nav2 parameters, robot and camera descriptions, rviz config, and the `cafe_table`, `objects` and `docks` models |
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
> **complete preservation of the environment**, not a per-project subset, and
> several of them are alternatives for the same scenario. One of them,
> `ir_movit_config/launch/ir_ur.py`, references an `ir_arena` package that does
> not exist anywhere upstream, so it could not have run as written. It is kept
> byte-identical and recorded rather than removed.

---

## What is deliberately not here

39 of the 207 upstream files are not published. None of them is needed to build or
run either project.

These are real assets authored by people other than the environment's author, with
no licence stated anywhere. The author's permission covers **his** work, not
theirs, so they are not published on the strength of it. All 39 are preserved in
full in the private snapshot described below, and they remain available in the
upstream repository itself, where their authors put them.

> The colcon build output under `ir_base/models/{build,install,log}/` **is**
> included here, byte-identical. It is the environment author's own generated
> output and so falls under the same permission; it also embeds his local
> filesystem path, which is his to publish — the upstream repository is public and
> has always carried it.

| Excluded | Author | Files | Where they are now |
|---|---|---|---|
| `ir_base/models/artag/` | **Nicola Castaman** `<nicola.castaman@dei.unipd.it>` | 36 | Replaced. The marker images are regenerated from the public AprilTag `tag36h11` family definition (BSD-2-Clause) — see [`NOTICE`](NOTICE) section 2a |
| `ir_base/models/walls/arena_walls/` | **Elisa Tosello** `<elisa.tosello@unipd.it>` — "Unipd Autonomous Robotics Arena Walls" | 3 | Not replaced. It is referenced by no world in either project |

The `walls` model is the one component of this environment that is **not present
in any form**. It is unused — no world file references it — so neither project is
affected, but the omission is stated here rather than left for a reader to find.

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

Every included file was verified by SHA-256 against the upstream commit after
copying:

| Check | Result |
|---|---|
| Files verified by SHA-256 | 168 / 168 |
| Content mismatches | 0 |
| Renames, reformats or edits | 0 |

The complete upstream snapshot — all 207 files, including the 39 not published —
with a per-file SHA-256 manifest, is held privately outside both repositories:

```
snapshot : ~/engineering-portfolio/work/third_party_inspect/ir_2526/
manifest : ~/engineering-portfolio/manifests/ir_2526-FULL.sha256   (207 entries)
```

> **This is not a byte-for-byte complete copy of the upstream repository**, and it
> is not described as one. It is a complete copy of the upstream repository's
> source, minus two asset groups authored by third parties with unresolved rights
> The exact 39 excluded paths are
> enumerated above.

---

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
**Piero Simonetto** (University of Padova), redistributed here with his permission.
Nothing in this repository claims that work as its author's.

`apriltag_ros` is the work of **Christian Rauch**, used under the MIT licence.

Full component-by-component status: [`NOTICE`](NOTICE).
