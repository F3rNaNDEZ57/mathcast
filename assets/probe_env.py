"""mathcast environment probe - run by /mathcast:init.

Reports what is actually present rather than assuming it. Three groups:

  toolchain  - Python packages, FFmpeg, LaTeX
  network    - whether IPv6 is advertised but unroutable (the black-hole fault)
  tts        - which speech services can actually be constructed

Prints a human-readable report and writes machine-readable JSON to stdout after
the marker line, so the agent can act on it without re-parsing prose.

Never hangs: every network probe is bounded by PROBE_TIMEOUT.
"""

from __future__ import annotations

import json
import platform
import shutil
import socket
import sys
import time

PROBE_TIMEOUT = 3.0  # seconds - a healthy connect is ~0.05s, a black-holed one 21s
PROBE_HOST = "translate.google.com"  # what gTTS actually talks to
PROBE_PORT = 443
SLOW_CONNECT = 1.0  # a connect slower than this is treated as a black-hole signal

result: dict = {"platform": {}, "toolchain": {}, "network": {}, "tts": {}}


def _ok(label: str, good: bool, detail: str = "") -> None:
    mark = "OK  " if good else "MISS"
    print(f"  [{mark}] {label}{(' - ' + detail) if detail else ''}")


print("\nplatform")
# Detect the package managers ACTUALLY present rather than inferring them from
# the OS. Manim's own docs decline to give per-distro instructions for exactly
# this reason - "we cannot give detailed instructions for all package managers"
# - so guessing apt from "Linux" would be guessing.
_system = platform.system()
_pm = [m for m in ("winget", "choco", "scoop", "brew", "apt-get", "dnf", "pacman", "zypper")
       if shutil.which(m)]
# Anything needing sudo must never be run unattended by an agent; it is handed to
# the user instead. winget and brew install without sudo (winget may raise its own
# UAC prompt, which is the user's own consent moment).
_needs_sudo = {"apt-get", "dnf", "pacman", "zypper"}
print(f"  system: {_system} {platform.release()}")
print(f"  package managers: {', '.join(_pm) if _pm else 'none found'}")
result["platform"] = {
    "system": _system,
    "release": platform.release(),
    "package_managers": _pm,
    "runnable_without_sudo": [m for m in _pm if m not in _needs_sudo],
    "needs_sudo": [m for m in _pm if m in _needs_sudo],
}

# ---------------------------------------------------------------- toolchain
print("\ntoolchain")
print(f"  [OK  ] Python {sys.version.split()[0]}")
result["toolchain"]["python"] = sys.version.split()[0]

for mod, label in [("manim", "Manim CE"), ("manim_voiceover", "manim-voiceover")]:
    try:
        m = __import__(mod)
        v = getattr(m, "__version__", "?")
        _ok(label, True, v)
        result["toolchain"][mod] = v
    except Exception as e:  # noqa: BLE001
        _ok(label, False, type(e).__name__)
        result["toolchain"][mod] = None

for exe, label in [("ffmpeg", "FFmpeg"), ("latex", "LaTeX")]:
    path = shutil.which(exe)
    _ok(label, bool(path), path or "not on PATH")
    result["toolchain"][exe] = path

# dvisvgm is what Manim actually uses to turn LaTeX into SVG; latex alone is not enough
dvisvgm = shutil.which("dvisvgm")
_ok("dvisvgm", bool(dvisvgm), dvisvgm or "not on PATH - MathTex will fail")
result["toolchain"]["dvisvgm"] = dvisvgm

# pycairo needs pkg-config to BUILD on macOS. Manim's install docs call it out
# explicitly; without it `pip install manim` fails while compiling pycairo.
if _system == "Darwin":
    _pc = shutil.which("pkg-config")
    _ok("pkg-config", bool(_pc), _pc or "not on PATH - pycairo will fail to build")
    result["toolchain"]["pkg-config"] = _pc

# pycairo needs these to BUILD on macOS. Manim's install docs call them out
# explicitly; without them `pip install manim` fails while compiling pycairo.
if _system == "Darwin":
    for exe in ("pkg-config",):
        path = shutil.which(exe)
        _ok(exe, bool(path), path or "not on PATH - pycairo will fail to build")
        result["toolchain"][exe] = path


# ------------------------------------------------------------------ network
print("\nnetwork")


def _connect(family: int, addr) -> float | None:
    """Return connect time in seconds, or None on failure/timeout."""
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(PROBE_TIMEOUT)
    t0 = time.time()
    try:
        s.connect(addr)
        return time.time() - t0
    except Exception:  # noqa: BLE001
        return None
    finally:
        s.close()


try:
    infos = socket.getaddrinfo(PROBE_HOST, PROBE_PORT, proto=socket.IPPROTO_TCP)
except Exception as e:  # noqa: BLE001
    print(f"  [MISS] DNS for {PROBE_HOST} failed: {e}")
    result["network"] = {"dns": False, "online": False, "ipv6_blackhole": None}
else:
    v6 = [i for i in infos if i[0] == socket.AF_INET6]
    v4 = [i for i in infos if i[0] == socket.AF_INET]
    v6_first = bool(infos) and infos[0][0] == socket.AF_INET6

    t6 = _connect(v6[0][0], v6[0][4]) if v6 else None
    t4 = _connect(v4[0][0], v4[0][4]) if v4 else None

    # The fault: IPv6 records exist and are tried first, but do not connect,
    # while IPv4 connects fine. Every HTTPS request then eats the SYN-retry budget.
    blackhole = bool(v6) and v6_first and (t6 is None or t6 > SLOW_CONNECT) and t4 is not None

    print(f"  IPv6 records: {len(v6)}   IPv4 records: {len(v4)}   IPv6 returned first: {v6_first}")
    print(f"  IPv6 connect: {('%.2fs' % t6) if t6 else 'TIMEOUT/FAIL'}")
    print(f"  IPv4 connect: {('%.2fs' % t4) if t4 else 'TIMEOUT/FAIL'}")
    if blackhole:
        print("  [WARN] IPv6 is advertised but unroutable - gTTS will cost ~85s per clip.")
    result["network"] = {
        "dns": True,
        "online": t4 is not None or t6 is not None,
        "ipv6_blackhole": blackhole,
        "ipv6_connect_s": t6,
        "ipv4_connect_s": t4,
    }


# ---------------------------------------------------------------------- tts
print("\ntts")
for mod, cls, label in [
    ("manim_voiceover.services.gtts", "GTTSService", "gTTS (cloud, default)"),
    ("kokoro_mv", "KokoroService", "Kokoro (local, offline)"),
    ("manim_voiceover.services.openai", "OpenAIService", "OpenAI (cloud, needs key)"),
]:
    try:
        __import__(mod)
        _ok(label, True)
        result["tts"][cls] = True
    except Exception as e:  # noqa: BLE001
        _ok(label, False, type(e).__name__)
        result["tts"][cls] = False

print("\n---MATHCAST-JSON---")
print(json.dumps(result, indent=2, default=str))
