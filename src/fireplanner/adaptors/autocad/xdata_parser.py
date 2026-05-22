class XDataParser:
    def parse(self, raw_xdata: list[str]) -> dict[str, str]:
        metadata = {}

        for item in raw_xdata:
            if "=" not in item:
                continue

            key, value = item.split("=", 1)

            key = key.strip()
            value = value.strip()

            if key:
                metadata[key] = value

        return metadata
