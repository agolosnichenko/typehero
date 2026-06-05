"""ASCII-art wordmark for the menu dashboard.

A hardcoded ANSI-shadow block; not generated at runtime. Lines are padded to
equal width so a centered render keeps the glyphs aligned as one block rather
than centering each row independently.
"""

from __future__ import annotations

BANNER = (
    "████████╗██╗   ██╗██████╗ ███████╗██╗  ██╗███████╗██████╗  ██████╗ \n"
    "╚══██╔══╝╚██╗ ██╔╝██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔═══██╗\n"
    "   ██║    ╚████╔╝ ██████╔╝█████╗  ███████║█████╗  ██████╔╝██║   ██║\n"
    "   ██║     ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██║██╔══╝  ██╔══██╗██║   ██║\n"
    "   ██║      ██║   ██║     ███████╗██║  ██║███████╗██║  ██║╚██████╔╝\n"
    "   ╚═╝      ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ \n"
).rstrip("\n")
