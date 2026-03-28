from fireplanner.geometry.primitives import Block, Point, PrimitiveStyle


def test_block_construction():
    center = Point(x=1.0, y=2.0, z=3.0)

    block = Block(name="Valve", center=center)

    assert block.name == "Valve"
    assert block.center == center
    assert block.style is None


def test_block_style_setter_and_getter():
    block = Block(name="Valve", center=Point(x=1.0, y=2.0, z=3.0))
    style = PrimitiveStyle(layer="A-BLOCK", color="cyan", category="device")

    block.style = style

    assert block.style == style


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


def test_block_to_json_and_from_json_with_style():
    style = PrimitiveStyle(layer="A-BLOCK", color="magenta", category="equipment")
    block = Block(
        name="Valve",
        center=Point(x=1.0, y=2.0, z=3.0),
        style=style,
    )

    data = block.to_json()

    assert data == {
        "Block": {
            "name": "Valve",
            "center": {"Point": "1.0, 2.0, 3.0"},
            "style": {
                "layer": "A-BLOCK",
                "color": "magenta",
                "category": "equipment",
            },
        }
    }
    assert Block.from_json(data).style == style
