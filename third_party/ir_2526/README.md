# Vendored simulation environment — `ir_2526`

The ROS 2 packages in this directory provide the Gazebo + MoveIt 2 simulation
environment that this project was built and tested against. They are **not part
of this project** and were **not written by its author**. They are vendored here
so the project can be built and run without cloning an external repository.

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

Every file in this directory is **byte-identical** to the file at that commit.
Nothing has been edited, reformatted, re-licensed or had its headers altered.
This was verified after copying by hashing each file against the upstream
snapshot — see `docs/UPSTREAM_DEPENDENCIES.md` in the repository root.

## Licence status — please read

**These files are NOT covered by this repository's Apache-2.0 licence.** The
`LICENSE` file at the repository root applies only to the project's own code.

They are redistributed here **with the permission of the original author**,
granted on the basis that proper attribution is maintained. No licence text was
supplied with the original work — upstream declares
`<license>TODO: License declaration</license>` in three of its five packages and
carries no `LICENSE` file at all. So the correct description of their status is:

> Redistributed with the author's permission. Copyright remains with the original
> authors. All rights reserved other than the redistribution expressly permitted.

If you intend to reuse these files in your own work, ask the original authors —
do not assume they are open source.

## Authorship and attribution

| Component | Author | Copyright / licence |
|---|---|---|
| `ir_launch` packages and launch files | Piero Simonetto | © Piero Simonetto |
| `ir_base` worlds, maps, parameters, URDFs | Piero Simonetto | © Piero Simonetto |
| `ir_movit_config` — MoveIt 2 configuration, controllers, SRDF, xacro | Piero Simonetto, generated with MoveIt Setup Assistant | © Piero Simonetto |
| `ir_desription` — UR5 + Robotiq description, meshes, kinematics | Piero Simonetto | © Piero Simonetto |
| `ir_base/models/artag/**` | **Nicola Castaman** `<nicola.castaman@dei.unipd.it>` | © Nicola Castaman |
| `ir_base/models/cafe_table/**` | **Nate Koenig** `<nate@osrfoundation.org>`, Open Robotics | © Nate Koenig / Open Robotics |
| UR5 meshes inside `ir_desription/meshes/ur5/**` | Universal Robots | BSD-3-Clause (`ur_description`) |
| Launch files derived from Universal Robots bringup | Stogl Robotics Consulting UG | BSD-3-Clause |
| Launch files derived from MoveIt / FZI | FZI Forschungszentrum Informatik | BSD-3-Clause |

The authorship of `artag` and `cafe_table` is recorded in each model's own
`model.config`, which is preserved unmodified.

## What is included

```
third_party/ir_2526/
├── README.md            this file
├── NOTICE               formal attribution and licence statement
├── ir_launch/           simulation entry point
│   └── launch/          assignment_2.launch.py
├── ir_base/             environment assets
│   ├── worlds/          iaslab_ur.sdf (the world this project runs in)
│   ├── params/          ur_bridge.yaml
│   ├── urdf/            (package scaffolding requires the directory)
│   └── models/          artag, cafe_table
├── ir_desription/       UR5 + Robotiq robot description
│   ├── urdf/            ur_gripper.urdf and the xacro includes
│   ├── meshes/ur5/      visual (.dae) and collision (.stl) meshes
│   └── config/          kinematics, joint limits, physical parameters
└── ir_movit_config/     MoveIt 2 configuration
    ├── launch/          ir_base.launch.py, ir_movit.launch.py, gazebo.launch.py
    ├── config/          controllers, kinematics, SRDF, xacro
    └── src/             short_joint_state_publisher
```

### Deliberately omitted

| Omitted | Reason |
|---|---|
| `ir_base/models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream — not part of the environment |
| `ir_base/models/docks`, `models/objects`, `models/walls` | **not referenced by the simulation world.** Omitting them limits how much third-party material is redistributed, since `models/walls/arena_walls` is credited to a further author (Elisa Tosello) and `objects`/`docks` carry no authorship at all |
| `apriltag_ros` | a pristine upstream copy of `apriltag_ros` 3.3.0 (MIT). Not used by this project, which detects tags with `dt_apriltags` in Python |

The world file was inspected for `model://` references: only `models/artag` and
`models/cafe_table` are required.

## Package names are unchanged

The packages keep their original names — `ir_launch`, `ir_base`,
`ir_desription`, `ir_movit_config` — because the launch files resolve them by
name via `FindPackageShare(...)` and `get_package_share_directory(...)`.
Renaming any of them would break the environment.

> `ir_desription` is spelled that way upstream (a typo for "description"). The
> spelling is preserved deliberately, because `ir_movit_config` and
> `ir_launch` reference it by that exact name.

## Building

`colcon` discovers packages recursively, so building from the repository root
picks these up automatically alongside the project's own package:

```bash
colcon build --symlink-install
```

To build only the project's own code:

```bash
colcon build --symlink-install --packages-select group29_assignment_2
```
