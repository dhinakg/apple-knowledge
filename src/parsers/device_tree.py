from io import BytesIO
from pathlib import Path
import sys

PROPERTY_NAME_LENGTH = 32


class ExpectedBytesIO(BytesIO):
    def read(self, size: int = -1):
        data = super().read(size)
        if len(data) != size:
            raise ValueError(f"Expected {size} bytes, got {len(data)}")
        return data


class DeviceTreeEntry:
    def __init__(self):
        self.properties: dict[str, bytes] = {}
        self.children: list[DeviceTreeEntry] = []

    @property
    def name(self):
        if "name" not in self.properties:
            return None
        return self.properties["name"].decode().rstrip("\x00")

    def __repr__(self) -> str:
        return f"<DeviceTreeEntry {self.name}>"


def parse_property(raw: BytesIO):
    name = raw.read(PROPERTY_NAME_LENGTH).decode().rstrip("\x00")
    # Not entirely sure why the length is masked with 0xFFFFFF
    length = int.from_bytes(raw.read(4), "little") & 0xFFFFFF
    value = raw.read(length)
    if length % 4:
        raw.read(4 - (length % 4))  # Padding
    return name, value


def parse_node(raw: BytesIO):
    node = DeviceTreeEntry()

    properties_count = int.from_bytes(raw.read(4), "little")
    children_count = int.from_bytes(raw.read(4), "little")

    for _ in range(properties_count):
        name, value = parse_property(raw)
        node.properties[name] = value

    if "name" not in node.properties:
        raise ValueError("Node does not have a name property")

    for _ in range(children_count):
        node.children.append(parse_node(raw))

    return node


def parse_device_tree(file: Path):
    with ExpectedBytesIO(file.read_bytes()) as raw:
        device_tree = parse_node(raw)
        # eof = raw.read()
        # assert not eof, f"EOF not reached: {eof}"
    return device_tree


def bytes_to_str(b):
    return b.decode().rstrip("\x00")


def process_device_tree(device_tree_path: Path):
    root = parse_device_tree(device_tree_path)

    model_identifier = bytes_to_str(root.properties["model"])
    target = bytes_to_str(root.properties["target-type"])
    compatible = [bytes_to_str(i) for i in root.properties["compatible"].split(b"\x00")[:-1]]
    boardconfig = compatible[0]

    assert boardconfig in [f"{target}AP", f"{target}DEV"], f"Boardconfig mismatch: {boardconfig} {target}"

    if "target-sub-type" in root.properties:
        assert bytes_to_str(root.properties["target-sub-type"]) == boardconfig, f"Boardconfig mismatch: {boardconfig}"

    assert compatible == [boardconfig, model_identifier, "AppleARM"] or compatible == [
        boardconfig,
        model_identifier,
        "AppleVirtualPlatformARM",
    ], "Compatible mismatch"

    product = next((i for i in root.children if i.name == "product"), None)
    assert product, "Product node not found"
    product_name = bytes_to_str(product.properties.get("product-name", b"")) or None
    product_description = bytes_to_str(product.properties.get("product-description", b"")) or None
    product_soc = bytes_to_str(product.properties.get("product-soc-name", b"")) or None

    result = {
        "model_identifier": model_identifier,
        "target": target,
        "boardconfig": boardconfig,
        "product_name": product_name,
        "product_description": product_description,
        "product_soc": product_soc,
    }

    return [result]


if __name__ == "__main__":
    process_device_tree(Path(sys.argv[1]))
