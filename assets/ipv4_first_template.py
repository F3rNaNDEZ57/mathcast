"""Force IPv4 address resolution for this process.

Why this exists
---------------
On this machine DNS advertises AAAA (IPv6) records for Google hosts, but IPv6 is
black-holed on the network: every IPv6 connect sits in Windows SYN retries for
~21 seconds and then fails, after which the client falls back to IPv4 and
succeeds in ~0.05s.

gTTS issues roughly four HTTPS requests per narration clip, so each clip cost
~85 seconds of dead waiting instead of ~2. Measured on 2026-09-17: a render with
20 narration blocks spent 46.8 minutes waiting and about 2 minutes rendering.

Importing this module filters IPv6 results out of ``socket.getaddrinfo`` for the
current process only. Nothing system-wide changes, no elevation is needed, and
any other process is unaffected.

The real fix is at the OS level, which also repairs every other tool on this
machine that talks to an IPv6-advertising host (pip, npm, git, browsers).
In an **elevated** prompt::

    netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 60 4

That raises IPv4's precedence above IPv6 without disabling IPv6. Undo with::

    netsh interface ipv6 reset prefixpolicy

Once that is in place this module becomes a no-op and can be dropped, along with
the ``import ipv4_first`` line in generated scenes.
"""

import socket

__all__ = ["enable", "disable", "is_enabled"]

_original_getaddrinfo = socket.getaddrinfo
_enabled = False


def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """getaddrinfo that drops IPv6 results, falling back if none remain."""
    results = _original_getaddrinfo(host, port, family, type, proto, flags)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    # If a host is genuinely IPv6-only, returning nothing would break it
    # outright - better to hand back what we got and let it try.
    return ipv4 or results


def enable():
    """Filter IPv6 out of name resolution for this process. Idempotent."""
    global _enabled
    if not _enabled:
        socket.getaddrinfo = _ipv4_only_getaddrinfo
        _enabled = True


def disable():
    """Restore the stdlib resolver."""
    global _enabled
    if _enabled:
        socket.getaddrinfo = _original_getaddrinfo
        _enabled = False


def is_enabled():
    return _enabled


# Importing is the intended usage - scenes just `import ipv4_first`.
enable()
