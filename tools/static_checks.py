#!/usr/bin/env python3
"""
Layer-0 static checks — run with no ROS installation.

    python3 tools/static_checks.py

Checks the repository is well-formed: syntax, manifests, launch references,
licence/attribution files, documentation links and anchors, and that no personal
data or credentials are present. Exits non-zero on failure, so it is usable as a
pre-commit hook or a CI step.

It does NOT prove the system builds or runs. See docs/TEST_PLAN.md for the layers
that do, and for what has and has not been executed.
"""
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS, FAIL = [], []

# Upstream defects inherited with the vendored environment. Named explicitly so a
# genuine new failure is never hidden behind a permanently red suite.
KNOWN_NON_COMPILING = {
    "third_party/ir_2526/ir_movit_config/launch/simulation_complete.launch.py",
}
KNOWN_MALFORMED_XML = {
    "third_party/ir_2526/ir_desription/urdf/ur_gripper_base.urdf",
}
# references to packages that do not exist anywhere upstream
KNOWN_UNRESOLVED_PKGS = {"ir_arena"}
STD_PKG_PREFIXES = ("ros_", "nav2_", "rviz", "moveit", "controller_", "joint_state",
                    "robot_state", "xacro", "ur_", "robotiq", "image_", "apriltag")


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))


def rel(p):
    return os.path.relpath(p, R)


def slug(h):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", h.strip().lower())
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE))


def main():
    # 1. python compiles
    py = [p for p in glob.glob(os.path.join(R, "**", "*.py"), recursive=True)
          if "/.git/" not in p]
    bad = [rel(p) for p in py if subprocess.run(
        [sys.executable, "-m", "py_compile", p], capture_output=True).returncode]
    unexpected = [b for b in bad if b not in KNOWN_NON_COMPILING]
    check(f"python syntax compiles ({len(py)} files, {len(bad) - len(unexpected)} known upstream defect)",
          not unexpected, str(unexpected[:3]))

    # 2. manifests
    pkgs = []
    for px in glob.glob(os.path.join(R, "**", "package.xml"), recursive=True):
        try:
            root = ET.parse(px).getroot()
            assert root.findtext("name")
            pkgs.append(root.findtext("name"))
        except Exception as e:
            check(f"package.xml well-formed: {rel(px)}", False, str(e))
    check(f"package.xml well-formed and named ({len(pkgs)} packages)", bool(pkgs),
          ", ".join(sorted(pkgs)))

    # 3. model / world XML
    xmls = [p for p in glob.glob(os.path.join(R, "**", "*.sdf"), recursive=True)
            + glob.glob(os.path.join(R, "**", "*.urdf"), recursive=True)
            if "/.git/" not in p]
    bad = []
    for p in xmls:
        try:
            ET.parse(p)
        except Exception:
            if rel(p) not in KNOWN_MALFORMED_XML:
                bad.append(rel(p))
    check(f"model/world XML parses ({len(xmls)} files, "
          f"{len(KNOWN_MALFORMED_XML & {rel(p) for p in xmls})} known upstream defect)",
          not bad, str(bad[:3]))

    # 4. launch package references
    refs = set()
    for lf in glob.glob(os.path.join(R, "**", "launch", "*.py"), recursive=True):
        t = open(lf, encoding="utf-8", errors="replace").read()
        refs |= set(re.findall(r"get_package_share_directory\(['\"]([^'\"]+)", t))
        refs |= set(re.findall(r"FindPackageShare\(['\"]([^'\"]+)", t))
    unres = sorted(p for p in refs if p not in pkgs
                   and p not in KNOWN_UNRESOLVED_PKGS
                   and not p.startswith(STD_PKG_PREFIXES))
    check(f"launch package references resolvable ({len(refs)} refs)", not unres,
          f"unresolved: {unres}" if unres else "")

    # 5. own-package executables declared
    declared_exe = set()
    for cml in glob.glob(os.path.join(R, "**", "CMakeLists.txt"), recursive=True):
        declared_exe |= set(re.findall(r"add_executable\((\w+)", open(cml).read()))
    py_srcs = {os.path.splitext(os.path.basename(p))[0]
               for p in glob.glob(os.path.join(R, "**", "*.py"), recursive=True)}
    used = set()
    for lf in glob.glob(os.path.join(R, "**", "launch", "*.py"), recursive=True):
        for m in re.finditer(r"package=['\"]([\w]+)['\"]\s*,\s*executable=['\"]([\w.]+)",
                             open(lf, encoding="utf-8", errors="replace").read()):
            if m.group(1) in pkgs:
                used.add(m.group(2))
    missing = sorted(e for e in used if e not in declared_exe
                     and os.path.splitext(e)[0] not in py_srcs)
    check(f"own-package launch executables declared ({len(used)} refs)", not missing,
          str(missing))

    # 6. documentation links and anchors
    mds = [p for p in glob.glob(os.path.join(R, "**", "*.md"), recursive=True)
           if "/.git/" not in p]
    anchors = {}
    for md in mds:
        hs = re.findall(r"^#{1,6}\s+(.+?)\s*$", open(md, encoding="utf-8").read(), re.M)
        anchors[rel(md)] = {slug(h) for h in hs}
    bad = []
    for md in mds:
        r_ = rel(md)
        base = os.path.dirname(r_)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)",
                             open(md, encoding="utf-8").read()):
            t = m.group(1)
            if t.startswith(("http", "mailto:")):
                continue
            if t.startswith("#"):
                if t[1:].lower() not in anchors[r_]:
                    bad.append(f"{r_} -> {t}")
                continue
            path, _, frag = t.partition("#")
            tgt = os.path.normpath(os.path.join(base, path)) if path else r_
            if not os.path.exists(os.path.join(R, tgt)):
                bad.append(f"{r_} -> {t}")
            elif frag and tgt.endswith(".md") and frag.lower() not in anchors.get(tgt, set()):
                bad.append(f"{r_} -> {t}")
    check(f"documentation links and anchors resolve ({len(mds)} files)", not bad,
          str(bad[:3]))

    # 7. personal data / credentials
    pat = re.compile(r"studenti\.unipd\.it|BEGIN (RSA|OPENSSH) PRIVATE|ghp_[A-Za-z0-9]{20}")
    hits = []
    for p in glob.glob(os.path.join(R, "**", "*"), recursive=True):
        if not os.path.isfile(p) or "/.git/" in p:
            continue
        try:
            if pat.search(open(p, encoding="utf-8", errors="ignore").read()):
                hits.append(rel(p))
        except Exception:
            pass
    check("no personal data or credentials", not hits, str(hits[:3]))

    # 8. licence / attribution present
    check("LICENSE + NOTICE + licence texts present",
          os.path.isfile(os.path.join(R, "LICENSE"))
          and os.path.isfile(os.path.join(R, "third_party/ir_2526/NOTICE"))
          and os.path.isdir(os.path.join(R, "third_party/ir_2526/licenses")))

    # 9. README completeness and the honesty invariant
    rd = open(os.path.join(R, "README.md"), encoding="utf-8").read()
    need = ["Installation", "Running", "Configuration", "Results",
            "Known limitations", "Reproducibility"]
    check("README has the required sections",
          all(n.lower() in rd.lower() for n in need),
          str([n for n in need if n.lower() not in rd.lower()]))
    check("README separates original runs from fresh verification",
          ("NOT RUN" in rd) and ("original" in rd.lower()))

    print()
    print(f"{len(PASS)} passed, {len(FAIL)} failed")
    for f in FAIL:
        print(f"   FAILED: {f}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
