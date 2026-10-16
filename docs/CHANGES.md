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
never tested*. That was wrong and is fixed. The [Results](../README.md#results) and
[Reproducibility status](../README.md#reproducibility-status) sections now separate two
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
The author's permission covers his own work; the scope question that raised was
put to the repository owner and answered at publication — see section 9 and
`docs/UPSTREAM_DEPENDENCIES.md`. The UR5 meshes are
**not** in that category — they are BSD-3-Clause from `ur_description` and are
redistributable with the attribution supplied in `NOTICE`.

**Also noted:** the world fetches one model from Gazebo Fuel
(`OpenRobotics/models/Sun`) on first run. Gazebo caches it, so it is a one-time
network requirement and it is not redistributed here.

## 9. Publication, and the consent record

**Published 2026-10-16.** Both consent gates that were open when the sections
above were written are now closed, and the repository is public.

1. **Collaborator consent.** `group29_assignment_2` was **led by Vaheid Labbaf**
   (8 commits to Ali Shavakhi's 6), and he is a co-author of the report: this
   repository presents his principal work. The repository owner confirmed on
   2026-10-16 that Vaheid Labbaf agreed to publication of the shared projects.
   Attribution stays accurate per path — see `../CONTRIBUTORS.md` and the *My
   contribution* section of the README, which states his share plainly rather
   than folding it into the owner's.
2. **Redistribution permission for the simulation environment.** The original
   author's permission to redistribute the environment files with attribution was
   confirmed on 2026-10-16, and the environment is vendored in section 8 above. A
   scope question was raised on the same day for the three items inside it that
   are credited to other authors (`models/artag`, `models/cafe_table`,
   `ir_desription/urdf/robotiq_d.urdf`); the owner authorised publication with
   those notices preserved unmodified. Their licence status remains documented,
   unresolved and unhidden in `UPSTREAM_DEPENDENCIES.md` and
   `../third_party/ir_2526/NOTICE`.

**Documentation corrected in the same pass**, after a verification run against
the live repository:

- *Known limitations* previously described the simulation environment as "not
  bundled" — true before section 8, false after it. Corrected.
- The reproducibility table listed "vendored code" as *verified absent*, which
  section 8 contradicts. Split into *secrets and personal data* (absent) and
  *vendored third-party code* (present, intentional, hashed).
- This section previously stated that collaborator consent had not been
  confirmed; it now records the consent that was obtained.
- **`robotiq_description` was missing from the install instructions.** The
  vendored `ir_desription/urdf/ur_gripper.urdf` — the model both launch paths
  load — resolves its gripper meshes as
  `package://robotiq_description/meshes/...`, and nothing in the repository
  provided that package, nor declared it in a `package.xml`, so `rosdep` would
  not have installed it either. Added to the prerequisites table and the `apt`
  list in the README, and to `RUNNING.md`. Every path, `urdf/` include and
  `config/` file the vendored description references was checked against the
  released `ros-<distro>-robotiq-description` package: all present, on both
  Humble and Jazzy.

## 10. Final cleanup pass — licensing, links and consistency

A review pass over the published state. Three groups of change.

**1. Third-party asset licensing resolved.** The asset group previously listed as an
open question is now settled on its own terms rather than on the environment
author's permission over other people's work:

- **`models/artag/**`** — previously credited to Nicola Castaman with no licence.
  The 18 marker images are now rendered from the public AprilTag `tag36h11` family
  definition (AprilRobotics, BSD-2-Clause), and the model wrapper and material
  scripts rewritten. Every image decodes to its own tag id under the reference
  detector, and its module-level pattern is identical to the file it replaces.
- **`models/cafe_table/**`** — licence verified as **CC-BY-3.0** (© 2012 Nathan
  Koenig, `osrf/gazebo_models`). Redistribution is permitted with attribution, so
  the model is kept and attributed in `third_party/ir_2526/NOTICE`, with the licence
  text in `third_party/ir_2526/licenses/`.

Full detail is in [`UPSTREAM_DEPENDENCIES.md`](UPSTREAM_DEPENDENCIES.md).

**2. Documentation defects corrected.** Three real defects were present on the
published pages, all introduced by earlier passes:

| Defect | Fix |
|---|---|
| The README contents list linked `#overview-and-objectives`, but the heading is `## Overview` | anchor corrected |
| Two references in this file linked `#results` and `#reproducibility-status`, which live in the README, not here | repointed at `../README.md#...` |
| `UPSTREAM_DEPENDENCIES.md` said "see the open question at the end" after that heading had been renamed | repointed at the resolved section |

**3. Presentation.** The contribution section now leads with the project's
engineering work and its authorship is stated plainly, pointing to
[`../CONTRIBUTORS.md`](../CONTRIBUTORS.md) for the full per-path attribution, which
is unchanged and remains the authoritative record for this repository.

No source file, vendored dependency, report or licence text was modified by this
pass.

