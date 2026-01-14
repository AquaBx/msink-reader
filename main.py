import sqlite3
import struct
import json
import sys

def removeChecksum(data):
    chunks, chunk_size = len(data), 255
    return b"".join(
        [data[i : i + chunk_size - 2] for i in range(0, chunks, chunk_size)]
    )

def read_bytes(data, ptr, size):
    return data[ptr : ptr + size], ptr + size

def read_byte(data, ptr):
    return data[ptr], ptr + 1

def read_varint(data, ptr):
    value = 0
    shift = 0

    while True:
        byte, ptr = read_byte(data, ptr)
        part = byte & 0b01111111
        value |= part << shift
        shift += 7

        if not (byte & 0b10000000):
            break

    return value, ptr

class Figure:
    def __init__(self, header1, id,timestamp, header2, points):
        self.id = id
        self.brush, self.group, _ = struct.unpack("BBB", header1)
        # self.x,self.y,ee = struct.unpack("ffB", header2)
        self.points = points

    def json(self, brushes, groups, page_number):
        pressures = [p.pressure for p in self.points]
        points = [[p.x, p.y] for p in self.points]
        return {
            "id":self.id,
            "type": "draw",
            "x": groups[self.group].offset_x,
            "y": groups[self.group].offset_y + page_number * 800,
            "strokeColor": "#" + brushes[self.brush].color.hex(),
            "points": points,
            "pressures": pressures,
            "simulatePressure": True,
        }

class Brush:
    def __init__(self, data):
        size, ptr = read_bytes(data, 0, 1)
        _, ptr = read_bytes(data, ptr, 1)
        self.color, ptr = read_bytes(data, ptr, 3)
        self.width, ptr = read_bytes(data, ptr, 4)
        self.height, ptr = read_bytes(data, ptr, 4)

class Point:
    def __init__(self, data):
        self.x, self.y, self.pressure, *r = struct.unpack("fffffff", data)

class Group:
    def __init__(self, data):
        _,self.skew_x,self.skew_y,_,self.offset_x,self.offset_y= struct.unpack("ffffff", data)

def parseFigure(data, ptr):
    id, ptr = read_varint(data, ptr)
    header1, ptr = read_bytes(data, ptr, 3)
    timestamp, ptr = read_varint(data, ptr)
    header2, ptr = read_bytes(data, ptr, 9)
    size, ptr = read_varint(data, ptr)

    pts = []

    for i in range(size):
        pt, ptr = read_bytes(data, ptr, 28)
        pts.append(Point(pt))


    return ptr, Figure(header1, id,timestamp, header2, pts)

file = sys.argv[1]
con = sqlite3.connect(file)
cur = con.cursor()

pages = cur.execute("SELECT id,page_order,bytes FROM pages JOIN blobs ON pages.id = blobs.owner_id WHERE ordinal = 2 ORDER BY page_order ASC").fetchall()

elements = []

for id,page_number,bytes in pages:
    bytes = removeChecksum(bytes)

    with open("bin.txt", "w") as f:
        f.write(bytes.hex())

    magick, ptr = read_bytes(bytes, 0, 18)
    print("magick", magick.hex())

    nb_color, ptr = read_varint(bytes, ptr)
    print("nb_colors", nb_color)

    brushes = []

    for i in range(nb_color):
        size = int.from_bytes(bytes[ptr : ptr + 1])
        
        if size == 0:
            size = 0x18

        color, ptr = read_bytes(bytes, ptr, size)
        brushes.append(Brush(color))

        if size == 0x18:
            ptr += 22

    nb_groups, ptr = read_varint(bytes, ptr)
    print("nb_groups", nb_groups)

    groups = []

    for i in range(nb_groups):
        group, ptr = read_bytes(bytes, ptr, 24)
        groups.append(Group(group))

    nb_polys, ptr = read_varint(bytes, ptr)

    print("nb_polys", nb_polys)
    for poly in range(nb_polys):
        ptr, fig = parseFigure(bytes, ptr)
        elements.append(fig.json(brushes,groups, page_number))

    with open("draw.excalidraw", "w") as f:
        f.write(
            json.dumps(
                {
                    "type": "excalidraw",
                    "version": 2,
                    "source": "https://excalidraw.com",
                    "elements": elements,
                    "appState": {
                        "gridSize": 20,
                        "gridStep": 5,
                        "gridModeEnabled": False,
                        "viewBackgroundColor": "#ffffff",
                        "lockedMultiSelections": {},
                    },
                    "files": {},
                }
            )
        )