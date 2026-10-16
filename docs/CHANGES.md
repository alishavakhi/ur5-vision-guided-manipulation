# Changes made during preparation

This repository was prepared from the private original
`alishavakhi/ws_29_assignments`. The original repository is **unmodified**.

This file records **every** change, so that nothing here is a silent edit.

---

## 1. Privacy and attribution — package manifest corrected

**File:** `src/group29_assignment_2/package.xml`

**Before:**

```xml
<description>Manipulation node for Assignment 2</description>
<maintainer email="TODO@todo.com">TODO</maintainer>
```

**After:** a description of what the package does, and

```xml
<maintainer email="45035448+alishavakhi@users.noreply.github.com">Ali Shavakhi</maintainer>
```

**Why:** the manifest still carried an unfilled `TODO` placeholder — the package
had no declared maintainer at all, which is a packaging defect. The replacement
uses the GitHub noreply address, which satisfies `package.xml`'s requirement for
an email attribute without publishing a personal address, and attributes the
package correctly.

The package's `<description>` also said only "Manipulation node for Assignment 2",
although this package contains four nodes including the entire vision pipeline.

---

## 2. Dependency declarations corrected — the most substantive fix

**File:** `src/group29_assignment_2/package.xml`

The original manifest declared **seven** dependencies, all for the C++ node. The
three Python nodes had **none of theirs declared**, and `rclpy` itself was
missing — so a clean machine could not reproduce this package even after a
successful build.

Added:

| Added | Needed by |
|---|---|
| `rclpy` | all three Python nodes — the entire Python side had no ROS client library declared |
| `sensor_msgs` | `tag_detector_node.py`, `color_detector_node.py` (`Image`, `CameraInfo`) |
| `std_msgs` | `cube_fusion_node.py`, `color_detector_node.py` (`String`, `Float32`) |
| `tf2_ros` | `tag_detector_node.py` (buffer, listener, broadcaster) |
| `cv_bridge` | `tag_detector_node.py`, `color_detector_node.py` |
| `python3-opencv` | `cv2` in both vision nodes |
| `python3-numpy` | all vision and filter maths |
| `python3-dt-apriltags` | `tag_detector_node.py` imports `dt_apriltags` (pip package; commented as such since it is not a rosdep key) |
| `moveit_msgs` | `manipulation_node.cpp` — `CollisionObject`, `Constraints`, `OrientationConstraint` |
| `shape_msgs` | `manipulation_node.cpp` — `SolidPrimitive` for the cube collision boxes |

The set was derived by reading every `import` in all four nodes and every
`#include` in the C++ file.

---

## 3. File reorganisation

| Original location | New location | Why |
|---|---|---|
| `Assignment2.pdf` (repo root) | `docs/reports/Group29_Assignment2_Report.pdf` | reports belong under `docs/`, and the file now says what it is |
| `src/group29_assignment_2/frames_2026-01-03_02.44.17.pdf` | `docs/figures/tf_tree_ur5_run.pdf` | a captured figure does not belong inside a package's source tree; renamed for what it shows |
| — | `docs/figures/tf_tree_ur5_run.png` | **added**: PNG rendering of the above, because GitHub renders PNG inline and PDF does not |

No source file was moved, renamed or deleted.

---

## 4. Added files

| File | Purpose |
|---|---|
| `README.md` | written for this repository |
| `LICENSE` (root) | Apache-2.0, copied from the package's own `LICENSE` — the licence already declared by the package |
| `.gitignore` | expanded; notably adds `venv/`, `venv*/`, `.venv/` |
| `CONTRIBUTORS.md` | collaborator attribution and commit-share record |
| `docs/RUNNING.md` | documents the external launch dependency |
| `docs/AI_USAGE_DISCLOSURE.md` | AI usage disclosure, carried over from the report |
| `docs/CHANGES.md` | this file |

The package's own `LICENSE` file was **kept** — a per-package licence is standard
ROS practice and `ament_copyright` lints expect it.

---

## 5. History

This repository begins from a **clean history**. The original repository's history
carries an entire Python virtual environment (numpy/scipy `.so` files, ~50 MB)
committed in `88bcfed` and deleted in `b8739ae` — gone from the tree but permanent
in history. Publishing it as-is would ship ~50 MB of binaries to every clone.

The original repository, its full history and its three branches
(`main`, `table-ali`, `vahid_work`) are untouched.

---

## What was deliberately NOT changed

- **No algorithm was modified.** The AprilTag pose recovery, the quaternion
  conversion, the ring-band colour mask, the hue classifier, the fusion windows
  and the entire manipulation sequence are exactly as found.
- **No threshold or parameter default was retuned.** The colour thresholds
  (`neutral_s_max = 35.0`, `black_v_max = 70.0`, `white_v_min = 185.0`, band
  kernels 6 px / 25 px) and the grasp offsets are untouched.
- **No file was reformatted or re-styled.** The C++ file's CRLF line endings were
  preserved.
- **The hard-coded manipulation sequence was not generalised.** It is documented
  as scene-specific in the README rather than rewritten.
- **The loose orientation tolerance (0.9 rad) was not tightened.** Changing it
  would alter motion planning behaviour that was never tested here.
- **No known limitation was fixed.** The colour name/confidence inconsistency, the
  single-shot operation and the literals in `base_link` are documented, not
  changed.

## 6. Report PDF: personal email addresses redacted

**File:** `docs/reports/Group29_Assignment2_Report.pdf`

Both authors' university email addresses appeared on the report's title line in
three places, and were removed from all three:

| Location | Before | After |
|---|---|---|
| Visible text (page 1) | `Email: <both addresses>` | `Email: redacted-for-privacy` |
| PDF link annotation | `<first address>` | removed |
| PDF link annotation | `<second address>` | removed |

(The addresses themselves are not reproduced in this file, since this file is
part of the public repository — quoting them here would undo the redaction.)

This is a genuine **text-level** redaction, not a black box drawn over the
addresses: the characters were removed from the page content stream, so the
addresses are not recoverable by extracting text, decompressing the streams, or
reading the file's raw bytes.

Verified after redaction:

- `pdftotext` output contains no occurrence of either address,
- decompressing every stream in the file finds no occurrence,
- the file's raw bytes contain no occurrence (the streams are Flate-compressed),
- neither `mailto:` annotation survives,
- document metadata is clean,
- the report is still 3 pages and renders correctly (checked visually).

**Authors' names were deliberately preserved** — `Ali Shavakhi, Vaheid Labbaf`
remains on the title line. Redacting an address must not erase attribution.

The report's **repository link annotation was repointed** at this public
repository (`https://github.com/alishavakhi/ur5-vision-guided-manipulation`).
It originally pointed at the private original `alishavakhi/ws_29_assignments`,
which would have returned 404 for a public reader. The demonstration-video link
annotation is untouched and still resolves.

## 7. Self-contained simulation investigation, and testing-documentation correction

**Investigated:** whether the simulation environment could be bundled so this
repository runs without cloning the course repository
(`github.com/PieroSimonet/ir_2526`).

**Outcome: it cannot lawfully be bundled.** The upstream repository carries
**no licence at all** — GitHub reports `license: null`, there is no `LICENSE`
file, and `ir_base`, `ir_launch` and `ir_desription` all declare
`<license>TODO: License declaration</license>`. Of the components this project
needs, **46 source files and 14 mesh assets are unlicensed** — the MoveIt
configuration, the SRDF, the UR5 and Robotiq description, the meshes, the Gazebo
world and the bridge configuration. Only three launch files and a `package.xml`
are BSD-3-Clause, and those alone would not make the project runnable.

A partial bundle of just the BSD-3-Clause files was considered and **rejected**:
`assignment_2.launch.py` immediately resolves `ir_movit_config` and
`ir_desription`, so it would fail at once, producing a repository that looks
self-contained but crashes. That is worse than a documented dependency.

**Note also:** `ir_movit_config` declares `BSD-3-Clause` in its `package.xml` but
ships **no licence text**, and its licence declaration is contradicted by its own
config files, which carry no licence at all. That inconsistency is why each file
was assessed from its own header rather than from the package declaration.

**Added:** `docs/UPSTREAM_DEPENDENCIES.md` — upstream repository and exact commit
SHA (`d19ae761`), the full component-by-component licence matrix, why nothing is
bundled, the two routes to self-containment, how to run it today against a pinned
commit, and attribution to the original author.

A complete local snapshot (209 files) of the upstream commit, with a per-file
SHA-256 manifest, was taken and preserved outside this repository.

**Corrected — testing documentation.** The previous version of this README said
`colcon build` and launching were "NOT TESTED", which misread as *the project was
never tested*. That was wrong and is fixed. The [Results](#results) and
[Reproducibility status](#reproducibility-status) sections now separate two
things explicitly:

| | |
|---|---|
| The original implementation in the original environment | **tested and working** — the cube swap completed and was recorded, with a live transform tree and the report as evidence |
| A fresh build and run of *this* repository | **not performed** here — no ROS 2 or MoveIt 2 on the preparation host |

No test result was invented; the change is in what the documentation claims.

**Expanded:** the install and run sections now cover Ubuntu and ROS 2 versions,
the full system dependency list including `dt-apriltags`, `colcon` build steps,
simulation startup, and a step-by-step description of what a successful run looks
like.

## 8. Simulation environment vendored — the repository is now self-contained

Following the author's permission, the simulation environment is now included in
this repository under `third_party/ir_2526/`. Cloning the external repository is
no longer required.

**Added** (136 files, byte-identical to upstream):

```
third_party/ir_2526/README.md        provenance, licence status, what's included
third_party/ir_2526/NOTICE           attribution for every author and project
third_party/ir_2526/ir_launch/       assignment_2.launch.py
third_party/ir_2526/ir_base/         world, params, models
third_party/ir_2526/ir_desription/   UR5 + Robotiq description and meshes
third_party/ir_2526/ir_movit_config/ MoveIt 2 configuration and controllers
```

**Deliberately not copied:**

| Excluded | Why |
|---|---|
| `models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream |
| `models/docks`, `models/objects`, `models/walls` | not referenced by the world; excluding them also limits third-party exposure, since `arena_walls` is credited to a further author |
| `apriltag_ros` | pristine upstream 3.3.0 (MIT); this project uses `dt_apriltags` instead, so it would be dead weight |

**Integrity:** all 136 files were hashed against the upstream snapshot after
copying and every one is identical. No header, copyright notice or licence
declaration was altered. Upstream package names — including the misspelled
`ir_desription` — are preserved, because the launch files resolve them by name.

**Licence boundary:** the root `LICENSE` (Apache-2.0) now explicitly states that
it covers only `src/`, `docs/` and the READMEs, and **not** `third_party/`. No
licence was invented for the vendored material — its status is "redistributed
with the author's permission, copyright remains with the original authors".

**Open items:** these files inside the required set are credited to other authors
and carry no stated licence — `models/artag` (Nicola Castaman), `models/cafe_table`
(Nate Koenig / Open Robotics) and `ir_desription/urdf/robotiq_d.urdf` (Robotiq).
The author's permission covers his own work; whether it extends to those is an
open question, recorded in `docs/UPSTREAM_DEPENDENCIES.md`. The UR5 meshes are
**not** in that category — they are BSD-3-Clause from `ur_description` and are
redistributable with the attribution supplied in `NOTICE`.

**Also noted:** the world fetches one model from Gazebo Fuel
(`OpenRobotics/models/Sun`) on first run. Gazebo caches it, so it is a one-time
network requirement and it is not redistributed here.

## Publication blockers — remaining

Only one blocker is left, and it is not a technical one:

1. **Collaborator consent.** `group29_assignment_2` was **led by Vaheid Labbaf**
   (8 commits to Ali Shavakhi's 6), who is also a co-author of the report. This
   repository presents his principal work. Consent to publish has **not** been
   confirmed, and it should not be made public until it is.
