from pathlib import Path

import rich
import yaml


from parsers import build_manifest, device_tree, restore
from utils.cache import CACHE_DIR



def sanitized_equal(d1: dict, d2: dict):
    common = set([i for i, v in d1.items() if v]) & set([i for i, v in d2.items() if v])
    return all(d1[k] == d2[k] for k in common)


def merge(existing, new):
    for i in new:
        if not new[i]:
            continue
        elif not existing.get(i):
            existing[i] = new[i]
        else:
            assert existing[i] == new[i], f"Conflict: {existing[i]} {new[i]}"
    return existing


def handle_device_trees():
    all = {}

    for dt_file in sorted(CACHE_DIR.rglob("DeviceTree.*")):
        if dt_file.suffix in [".im4p", ".img3"]:
            continue

        to_add = device_tree.process_device_tree(dt_file)
        for entry in to_add:
            if entry["boardconfig"] in all:
                if entry["boardconfig"] == "J42dAP":
                    # Keep the one with product_name and product_description
                    if entry["product_name"] and entry["product_description"]:
                        all[entry["boardconfig"]] = entry
                    continue
                elif entry["boardconfig"] in ["J327AP", "J327DEV"]:
                    # Keep the one with product_name not 0
                    if entry["product_name"] != "0":
                        all[entry["boardconfig"]] = entry
                    continue
                # assert (
                #     all[entry["boardconfig"]] == entry
                # ), f"Duplicate boardconfig: {entry['boardconfig']} {entry} {all[entry['boardconfig']]}"
                merge(all[entry["boardconfig"]], entry)
            else:
                all[entry["boardconfig"]] = entry

    rich.print(all)

def hexint_presenter(dumper, data):
    return dumper.represent_int(hex(data))


yaml.add_representer(int, hexint_presenter)

def handle_build_manifests():
    all = {}

    for bm_file in sorted(CACHE_DIR.rglob("BuildManifest.plist")):
        to_add = build_manifest.process_build_manifest(bm_file)

        for entry in to_add:
            if entry["boardconfig"] in all:
                # assert (
                #     all[entry["boardconfig"]] == entry
                # ), f"Duplicate boardconfig: {entry['boardconfig']} {entry} {all[entry['boardconfig']]}"
                merge(all[entry["boardconfig"]], entry)
            else:
                all[entry["boardconfig"]] = entry

    for i, v in all.items():
        print(f"CPID:{v['chip']} BORD:{v['board']} {v['boardconfig']} {v['model_identifier']}")

        # print(
        #     "\n".join(
        #         [
        #             ("      " + i)
        #             for i in yaml.dump(
        #                 {
        #                     int(v['board'], 16): {
        #                         "product_name": '',
        #                         "product_id": v['model_identifier'],
        #                         "board_name": v['boardconfig'],
        #                     }
        #                 },
        #                 sort_keys=False,
        #             ).splitlines()
        #         ]
        #     )
        # )


    rich.print(all)


def handle_restores():
    all = {}

    for restore_file in sorted(CACHE_DIR.rglob("Restore.plist")):
        to_add = restore.process_restore(restore_file)

        for entry in to_add:
            if entry["boardconfig"] in all:
                # assert (
                #     all[entry["boardconfig"]] == entry
                # ), f"Duplicate boardconfig: {entry['boardconfig']} {entry} {all[entry['boardconfig']]}"
                merge(all[entry["boardconfig"]], entry)
            else:
                all[entry["boardconfig"]] = entry

    rich.print(all)


def main():
    handle_device_trees()
    handle_build_manifests()
    handle_restores()


if __name__ == "__main__":
    main()
