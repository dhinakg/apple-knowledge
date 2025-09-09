import plistlib
import sys
from pathlib import Path


def process_restore(manifest_path: Path):
    manifest = plistlib.loads(manifest_path.read_bytes())
    results = []

    for device in manifest["DeviceMap"]:
        chip = device.get("CPID")
        board = device.get("BDID")
        boardconfig = device["BoardConfig"]
        platform = device["Platform"]

        result = {
            "boardconfig": boardconfig,
            "chip": chip,
            "board": board,
            "platform": platform,
        }

        results.append(result)

    return results


if __name__ == "__main__":
    process_restore(plistlib.loads(Path(sys.argv[1]).read_bytes()))
