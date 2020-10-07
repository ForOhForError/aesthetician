ancestry_map_decode = {
    0x1: 'hyur',
    0x2: 'elezen',
    0x3: 'lalafell',
    0x4: "miqo'te",
    0x5: "roegadyn",
    0x6: "au ra",
    0x7: "hrothgar",
    0x8: "viera",
}

ancestry_map_encode = {v: k for k, v in ancestry_map_decode.items()}

def ancestry_encode(value):
    value = value.lower()
    return ancestry_map_encode.get(value, 0x0)

def ancestry_decode(data):
    data = int.from_bytes(data, byteorder='little')
    return ancestry_map_decode.get(data, 'unknown')

gender_map_decode = {
    0x0: 'male',
    0x1: 'female'
}

gender_map_encode = {v: k for k, v in gender_map_decode.items()}

def gender_encode(value):
    value = value.lower()
    return gender_map_encode.get(value, 0x0)

def gender_decode(data):
    data = int.from_bytes(data, byteorder='little')
    return gender_map_decode.get(data, 'unknown')