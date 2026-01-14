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

BRUSH_CONFIG = {
    # --- PEN ---
    0x00: {"size": 46, "type": "Pen", "pressure": True},
    0x18: {"size": 46, "type": "Pen", "pressure": False},
    
    # --- PENCIL ---
    0x02: {"size": 46, "type": "Pencil", "pressure": True},
    0x1A: {"size": 46, "type": "Pencil", "pressure": False},

    # --- HIGHLIGHTER ---
    0x05: {"size": 29, "type": "Highlighter", "pressure": True},
    0x1D: {"size": 29, "type": "Highlighter", "pressure": False},
}

class Figure:
    def __init__(self, id,brush, group, points):
        self.id = id
        self.brush = brush
        self.group = group
        self.points = points

    @staticmethod
    def parse(data, ptr):
        id       , ptr = read_varint(data, ptr)
        brush    , ptr = read_varint(data, ptr)
        group    , ptr = read_varint(data, ptr)
        header1  , ptr = read_bytes(data, ptr, 1)
        timestamp, ptr = read_varint(data, ptr)
        header2  , ptr = read_bytes(data, ptr, 9)
        size     , ptr = read_varint(data, ptr)

        pts = []
        for i in range(size):
            pt, ptr = Point.parse(data, ptr)
            pts.append(pt)

        return ptr, Figure(id,brush,group,pts)

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
    def __init__(self, type,color,width,height):
        self.type = type
        self.color = color
        self.width = width
        self.height = height

    @staticmethod
    def parse(data, ptr):
        type,ptr = read_byte(data,ptr)
        _, ptr = read_byte(data, ptr)

        conf = BRUSH_CONFIG[type]

        color, ptr = read_bytes(data, ptr, 3)
        width, ptr = read_bytes(data, ptr, 4)
        height, ptr = read_bytes(data, ptr, 4)

        _, ptr = read_bytes(data, ptr, conf["size"] - (4+4+3+1+1))

        return Brush(type,color,width,height), ptr

class Point:
    def __init__(self, data):
        self.x, self.y, self.pressure, *r = struct.unpack("fffffff", data)

    @staticmethod
    def parse(data, ptr):
        pt, ptr = read_bytes(data, ptr, 28)
        return Point(pt), ptr

class Group:
    def __init__(self, data):
        _,self.skew_x,self.skew_y,_,self.offset_x,self.offset_y= struct.unpack("ffffff", data)
    
    @staticmethod
    def parse(data, ptr):
        gr, ptr = read_bytes(data, ptr, 24)
        return Group(gr), ptr

file = sys.argv[1]
con = sqlite3.connect(file)
cur = con.cursor()

pages = cur.execute("SELECT id,page_order,bytes FROM pages JOIN blobs ON pages.id = blobs.owner_id WHERE ordinal = 2 ORDER BY page_order ASC").fetchall()

elements = []

for id,page_number,bytes in pages:
    bytes = removeChecksum(bytes)

    with open("bin.txt", "w") as f:
        f.write(bytes.hex())

    header, ptr = read_bytes(bytes, 0, 18)
    print("header", header.hex())

    nb_color, ptr = read_varint(bytes, ptr)
    print("nb_colors", nb_color)

    brushes = []
    for i in range(nb_color):
        brush, ptr = Brush.parse(bytes,ptr) 
        brushes.append(brush)

    nb_groups, ptr = read_varint(bytes, ptr)
    print("nb_groups", nb_groups)

    groups = []
    for i in range(nb_groups):
        group, ptr = Group.parse(bytes,ptr) 
        groups.append(group)

    nb_polys, ptr = read_varint(bytes, ptr)
    print("nb_polys", nb_polys)

    for poly in range(nb_polys):
        ptr, fig = Figure.parse(bytes, ptr)
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