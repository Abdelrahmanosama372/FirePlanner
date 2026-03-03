from fireplanner.geometry.primitives import Block, Point


def test_block_construction():
    center = Point(x=1.0, y=2.0, z=3.0)

    block = Block(name="Valve", center=center)

    assert block.name == "Valve"
    assert block.center == center


def test_block_to_json():
    block = Block(name="Valve", center=Point(x=1.0, y=2.0, z=3.0))

    data = block.to_json()

    assert data == {
        "Block": {
            "name": "Valve",
            "center": {"Point": "1.0, 2.0, 3.0"},
        }
    }


def test_block_from_json():
    data = {
        "Block": {
            "name": "Valve",
            "center": {"Point": "1.0, 2.0, 3.0"},
        }
    }

    block = Block.from_json(data)

    assert block.name == "Valve"
    assert block.center == Point(x=1.0, y=2.0, z=3.0)
