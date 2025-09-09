import plistlib
import sys
from pathlib import Path


def process_build_manifest(manifest_path: Path):
    manifest = plistlib.loads(manifest_path.read_bytes())
    results = []

    for identity in manifest["BuildIdentities"]:
        chip = identity.get("ApChipID")
        board = identity.get("ApBoardID")
        security_domain = identity.get("ApSecurityDomain")
        device_class = identity["Info"]["DeviceClass"]
        model_identifier = identity.get("Ap,ProductType")

        # Not always present
        if "Ap,Target" in identity:
            boardconfig: str = identity["Ap,Target"]
            assert boardconfig.replace("MacAP", "AP").lower() == device_class.lower(), f"Boardconfig mismatch: {boardconfig}"
        else:
            # Bad capitalization
            boardconfig = device_class

        if "Ap,TargetType" in identity:
            assert boardconfig.lower() in [
                identity["Ap,TargetType"].lower() + "ap",
                identity["Ap,TargetType"].lower() + "dev",
            ], f"Boardconfig mismatch: {boardconfig}"

        result = {
            "model_identifier": model_identifier,
            "boardconfig": boardconfig,
            "chip": chip,
            "board": board,
            "security_domain": security_domain,
        }

        if not chip or not board:
            print(f"[{boardconfig}] Missing chip or board: {chip} {board}")

        for key in identity:
            if key in ["ApChipID", "ApBoardID"]:
                continue
            if (
                key in ["BoardID", "ChipID"]
                or "Board" in key
                # and key.replace("Board", "Chip") in identity
                and key not in ["BMU,BoardID", "Rap,BoardID"]
                and "Baobab" not in key
                and "Timer" not in key
                and "PCON" not in key
                and "USBPortController" not in key
                and "Yonkers" not in key
            ):
                print(f"[{boardconfig}] {key}: {identity[key]}")
                chip_key = key.replace("Board", "Chip")
                if chip_key in identity:
                    print(f"[{boardconfig}] {chip_key}: {identity[chip_key]}")
                else:
                    print(f"[{boardconfig}] Missing chip key: {chip_key}")

        if not chip or not board or int(chip, 16) in [0, 0xFF, 0xFFFF] or int(board, 16) in [0, 0xFF, 0xFFFF]:
            possibles = {i for i in identity if any(j in i for j in ["ChipID", "BoardID", "Domain"])}
            all_possibles = possibles.copy()
            possibles -= {
                "ApChipID",
                "ApBoardID",
                "ApSecurityDomain",
                "BbChipID",
            }
            # if len({i for i in possibles if "ChipID" in i}) == 1:
            #     pass
            # else:
            #     possibles -= {
            #         "BbChipID",
            #         "SE,ChipID",
            #         "Savage,ChipID",
            #         "eUICC,ChipID",
            #         "BMU,BoardID",
            #         "Rap,BoardID",
            #     }
            #     possibles = {
            #         key
            #         for key in possibles
            #         if "Baobab" not in key
            #         and "Timer" not in key
            #         and "PCON" not in key
            #         and "USBPortController" not in key
            #         and "Yonkers" not in key
            #     }
            if possibles:
                print(f"[{boardconfig}] Possibles: {sorted(possibles)} ({sorted(all_possibles)})")

        results.append(result)

    return results


if __name__ == "__main__":
    process_build_manifest(Path(sys.argv[1]))
