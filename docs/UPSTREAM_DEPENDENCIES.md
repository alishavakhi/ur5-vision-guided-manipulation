# Simulation environment — provenance, permission and licensing

This project runs in a Gazebo + MoveIt 2 simulation environment **written by
someone else**. It is vendored into this repository under
[`third_party/ir_2526/`](../third_party/ir_2526/) so the project can be built and
run without cloning an external repository. This document records where it came
from, what permission exists, and — importantly — what is **not** covered.

---

## Provenance

```
Upstream repository : https://github.com/PieroSimonet/ir_2526
Upstream commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Commit date         : 2025-09-10 16:23:42 +0200
Commit author       : pierosimonet <simonetto.piero@gmail.com>
Default branch      : main (the only branch)
Vendored on         : 2026-10-16
```

Every vendored file is **byte-identical** to that commit. Verified by hashing all
136 files against the upstream snapshot after copying — no header, copyright
notice or licence declaration was altered.

A complete snapshot of the upstream commit (209 files) with a per-file SHA-256
manifest is also held outside this repository, so the exact environment is
recoverable independently of both repositories.

## Permission

The environment is redistributed here **with the permission of the original
author, Piero Simonetto**, granted on the basis that attribution is maintained.

The upstream repository carries **no licence**: GitHub reports `license: null`,
there is no `LICENSE` file at its root, and `ir_base`, `ir_launch` and
`ir_desription` each declare `<license>TODO: License declaration</license>` in
their `package.xml`. No licence is asserted for the vendored material, and none
was invented. Its status is:

> Redistributed with the author's permission. Copyright remains with the original
> authors. All rights reserved other than the redistribution expressly permitted
> here.

The vendored files are therefore **not** covered by this repository's Apache-2.0
licence, which applies only to `src/`, `docs/` and the READMEs.

## Third-party components inside the environment — resolved

Two asset groups inside the vendored environment were not the author's to license,
and neither is published on the strength of his permission. Both were dealt with on
their own terms.

### 1. AprilTag marker images — regenerated from permissive data

`ir_base/models/artag/**` was previously credited to **Nicola Castaman** with no
licence stated anywhere — not in `model.config`, not in the repository. It has been
replaced rather than published on someone else's permission.

The 18 marker images are now rendered from the public AprilTag `tag36h11` family
definition — the codewords and bit layout published in
[`AprilRobotics/apriltag`](https://github.com/AprilRobotics/apriltag), licensed
**BSD-2-Clause** (© 2013–2016 The Regents of The University of Michigan). The images
distributed here are this project's own rendering of that permissively licensed
data. `model.sdf`, `model.config` and the 16 OGRE material scripts were rewritten as
equivalent functional files for the same reason.

Compatibility was verified rather than assumed:

| Check | Result |
|---|---|
| Every image decodes to its own tag id, using the reference AprilTag detector | 18 / 18 |
| Module-level black/white pattern identical to the file it replaces | 18 / 18 |
| Pixel difference against the file it replaces | 0–2 anti-aliased edge pixels in 8 of 18, 0 elsewhere |
| Geometry, material names, file names and directory layout | unchanged |

The two markers the simulation actually places in the world are `tag36h11` ids
**1** and **10**, which is exactly what the detector is configured to look for.

The previous files remain in this repository's git history, credited to their
original author. Nothing was removed from history.

### 2. Cafe table model — CC-BY-3.0, redistributed with attribution

`ir_base/models/cafe_table/**` is not a course asset at all. It is the `cafe_table`
model from [`osrf/gazebo_models`](https://github.com/osrf/gazebo_models), licensed
**Creative Commons Attribution 3.0 Unported**, © 2012 Nathan Koenig.

That licence expressly permits redistribution provided attribution is given, so the
model is kept unchanged and attributed in
[`third_party/ir_2526/NOTICE`](../third_party/ir_2526/NOTICE), with the licence text
in `third_party/ir_2526/licenses/CC-BY-3.0.txt`.

| Check | Result |
|---|---|
| `meshes/cafe_table.dae` against upstream | byte-identical |
| `materials/textures/Maple.jpg`, `Wood_Floor_Dark.jpg` against upstream | byte-identical |
| `.sdf` against upstream | one URI differs (`model://` vs `file://models/`) — a path fix by the vendor, not content |

### Components not affected by any of this

The UR5 meshes are BSD-3-Clause from Universal Robots' `ur_description` and are
redistributable with the attribution supplied in the `NOTICE`. The vendored launch
files derive from Nav2 (Apache-2.0), Stogl Robotics Consulting UG (BSD-3-Clause) and
PickNik / FZI (BSD-3-Clause), each with its notice intact inside the file.


## What is vendored, and what was left out

### Included

```
third_party/ir_2526/                                        136 files, 8.5 MB
├── ir_launch/          assignment_2.launch.py
├── ir_base/            worlds/ params/ urdf/ models/{artag,cafe_table}
├── ir_desription/      urdf/ meshes/ur5/ config/
└── ir_movit_config/    launch/ config/ src/ .setup_assistant
```

| Component | Role |
|---|---|
| `ir_base/worlds/iaslab_ur.sdf` | the world this project runs in |
| `ir_base/params/ur_bridge.yaml` | ROS–Gazebo bridge topics for the UR scene |
| `ir_desription/urdf/ur_gripper.urdf` | the UR5 + Robotiq model that `manipulation_node` plans for |
| `ir_desription/meshes/ur5/` | the arm's visual and collision geometry |
| `ir_desription/config/` | kinematics, joint limits and physical parameters |
| `ir_movit_config/config/` | controllers, `ur_gripper.srdf`, kinematics, xacro |
| `ir_movit_config/launch/` | `ir_base.launch.py`, `ir_movit.launch.py`, `gazebo.launch.py` |
| `ir_movit_config/src/` | `short_joint_state_publisher` |

### Deliberately excluded

| Excluded | Why |
|---|---|
| `ir_base/models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream — not part of the environment |
| `ir_base/models/docks`, `models/objects`, `models/walls` | **not referenced by the world.** Excluding them also reduces third-party exposure: `models/walls/arena_walls` is credited to a further author (Elisa Tosello) and `objects`/`docks` carry no authorship at all |
| `apriltag_ros` | a pristine copy of upstream `apriltag_ros` 3.3.0 (MIT). This project detects tags with `dt_apriltags` in Python and does not use it |

The world file was inspected for `model://` references: only `models/artag` and
`models/cafe_table` are required. Nothing omitted is needed to run the project.

## Package names are unchanged

The packages keep their original names — `ir_launch`, `ir_base`,
`ir_desription`, `ir_movit_config` — because the launch files resolve them by name
via `FindPackageShare(...)` and `get_package_share_directory(...)`. Renaming any
of them would break the environment.

> `ir_desription` is spelled that way upstream (a typo for "description"). The
> spelling is preserved deliberately, because `ir_movit_config` and `ir_launch`
> reference it by that exact name.

## Still required from the system

Standard ROS 2 packages only, installed through `rosdep`/`apt`:

`moveit`, `ros2-control`, `ros2-controllers`, `controller-manager`,
`cv-bridge`, `vision-opencv`, `ros-gz`, `ur-description`, `python3-opencv`,
`python3-numpy`, plus `dt-apriltags` from pip.

## One-time network access

The world includes a model fetched from Gazebo Fuel
(`https://fuel.gazebosim.org/1.0/OpenRobotics/models/Sun`). Gazebo caches Fuel
models after the first download, so this is required once and then works offline.
It is **not** redistributed here — it is fetched from upstream under its own
licence.

## Third-party scope question — raised, and answered on publication

The professor's permission covers **his** work. Three items inside the required
set were authored by other people and carry no stated licence:

- `ir_base/models/artag` — © Nicola Castaman
- `ir_base/models/cafe_table` — © Nate Koenig / Open Robotics
- `ir_desription/urdf/robotiq_d.urdf` — Robotiq

This was put to the repository owner before publication; on 2026-10-16
publication was authorised on the basis that these files form part of the
environment being redistributed with the original author's permission, with every
authorship notice preserved verbatim.

Stated plainly, so nothing here reads as a licence it is not:

- these items carry **no licence text of their own**. None was invented for them,
  and they are not covered by this repository's Apache-2.0 licence;
- they are included unmodified, with their authors' own notices exactly as
  upstream wrote them, and recorded in `../third_party/ir_2526/NOTICE`;
- if the question is ever revisited, `models/artag` can be regenerated from the
  public AprilTag `36h11` family definition (AprilRobotics, BSD-2-Clause) as
  original work; `models/cafe_table` can be replaced with an equivalent table
  model from a permissively licensed source; and the Robotiq gripper description
  can be taken from `robotiq_description` (BSD-3-Clause, PickNik) — which this
  repository now installs from the distribution anyway, for the meshes.
  Each is a one-commit change.

Everything else is either the professor's own work under his permission, or
permissively licensed with its notice intact — notably the UR5 meshes, which are
BSD-3-Clause from `ur_description` and are redistributable with the attribution
provided in `third_party/ir_2526/NOTICE`.

## Attribution

The simulation environment — the UR5 and Robotiq description, the MoveIt 2
configuration, the Gazebo world and the bridge configuration — is the work of its
original author, **Piero Simonetto** (University of Padova). Nothing in this
repository claims that work, and it is used unmodified.

The upstream launch files are themselves derived from:

- **Stogl Robotics Consulting UG (haftungsbeschränkt)** — BSD-3-Clause, author of
  the Universal Robots ROS 2 bringup launch files
- **PickNik, Inc.** — BSD-3-Clause
- **FZI Forschungszentrum Informatik** — BSD-3-Clause
- **Universal Robots** — BSD-3-Clause (`ur_description`)
- **AprilTag / AprilRobotics** — BSD-2-Clause (tag family definitions)
