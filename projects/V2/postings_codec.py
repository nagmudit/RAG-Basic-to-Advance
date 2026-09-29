"""Chapter 8's small variable-byte gap codec (separate from V2's RAM index).

Each positive gap is split into big-endian 7-bit groups; the final byte sets
its high bit. Positions, term frequency and field identity are NOT encoded by
this miniature docID-only example.
"""


def encode_positive(number):
    if not isinstance(number, int) or number < 1:
        raise ValueError("gap must be a positive integer")
    groups = [number & 0x7F]
    number >>= 7
    while number:
        groups.append(number & 0x7F)
        number >>= 7
    groups.reverse()
    groups[-1] |= 0x80
    return bytes(groups)


def encode_docids(docids):
    previous = 0
    result = bytearray()
    for docid in docids:
        if not isinstance(docid, int) or docid <= previous:
            raise ValueError("docIDs must be positive and strictly increasing")
        result.extend(encode_positive(docid - previous))
        previous = docid
    return bytes(result)


def decode_docids(data):
    current = 0
    previous = 0
    result = []
    pending = False
    for byte in data:
        current = (current << 7) | (byte & 0x7F)
        if byte & 0x80:
            if current == 0:
                raise ValueError("zero gap is invalid")
            previous += current
            result.append(previous)
            current = 0
            pending = False
        else:
            pending = True
    if pending:
        raise ValueError("unterminated variable-byte integer")
    return result


if __name__ == "__main__":
    example = [3, 8, 138]
    encoded = encode_docids(example)
    print(f"docIDs={example} gaps=[3, 5, 130] bytes={encoded.hex(' ')} "
          f"decoded={decode_docids(encoded)}")
