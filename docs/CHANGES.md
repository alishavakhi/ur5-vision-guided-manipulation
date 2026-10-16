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

## Publication blockers — remaining

Only one blocker is left, and it is not a technical one:

1. **Collaborator consent.** `group29_assignment_2` was **led by Vaheid Labbaf**
   (8 commits to Ali Shavakhi's 6), who is also a co-author of the report. This
   repository presents his principal work. Consent to publish has **not** been
   confirmed, and it should not be made public until it is.
