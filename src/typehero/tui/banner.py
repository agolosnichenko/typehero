"""ASCII-art wordmark for the menu dashboard (pyfiglet, ansi_shadow font).

Lines are padded to equal width so a centered render keeps the glyphs aligned
as one block rather than centering each row independently.
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
