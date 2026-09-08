"""Minimal adb helper for auto-detecting a locally connected Android device."""

import subprocess


def get_connected_android_udid() -> str:
    """Return the udid of the single Android device attached via `adb devices`.

    Raises RuntimeError if zero or more than one device is connected.
    """
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
    lines = [line for line in result.stdout.splitlines()[1:] if line.strip().endswith("\tdevice")]

    if not lines:
        raise RuntimeError("No Android device connected. Run `adb devices` to check.")

    udids = [line.split("\t")[0] for line in lines]
    if len(udids) > 1:
        raise RuntimeError(
            f"Multiple Android devices connected: {udids}. "
            "Set UDID in .env, or use --device=<name> from config/devices_config.json."
        )
    return udids[0]
