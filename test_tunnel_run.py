"""Manual tunnel smoke-run helper.

This module is intentionally side-effect free on import so pytest/IDEs don't
accidentally start tunnels during collection.
"""

from kater.tunnel import start_cloudflared, start_tailscale_funnel


def main() -> None:
    start_cloudflared()
    start_tailscale_funnel()


if __name__ == "__main__":
    main()
