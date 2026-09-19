#!/usr/bin/env python3
"""アプリアイコンを生成する（外部ライブラリ不要）。黒地に、月のマス目。
  python3 make_icons.py
"""
import struct, zlib, os

BG   = (0x00, 0x00, 0x00)
ON   = (0xF4, 0xEC, 0xDC)   # 入っている日
OFF  = (0x4A, 0x46, 0x3C)   # 空いている日
BAR  = (0x8D, 0xB4, 0xDA)   # 上の帯（曜日）

def blend(d, s, a): return tuple(round(x*(1-a) + y*a) for x, y in zip(d, s))

def rrect(px, w, h, x0, y0, x1, y1, r, color, alpha=1.0):
    for y in range(max(0,int(y0)), min(h,int(y1)+1)):
        for x in range(max(0,int(x0)), min(w,int(x1)+1)):
            cx = x0+r if x < x0+r else (x1-r if x > x1-r else x)
            cy = y0+r if y < y0+r else (y1-r if y > y1-r else y)
            if (x-cx)**2 + (y-cy)**2 > r*r: continue
            px[y][x] = blend(px[y][x], color, alpha)

FILLED = {(0,1),(0,3),(1,0),(1,2),(1,3),(2,1),(2,2)}   # 出勤が入っている日

def render(s):
    px = [[BG]*s for _ in range(s)]
    x0, x1 = 0.20*s, 0.80*s
    gap = 0.035*s
    cell = (x1-x0-gap*3)/4
    top = 0.235*s
    rrect(px, s, s, x0, top, x1, top+cell*0.42, cell*0.20, BAR)   # 帯
    gy = top + cell*0.42 + gap*1.4
    for r_ in range(3):
        for c in range(4):
            x = x0 + c*(cell+gap); y = gy + r_*(cell+gap)
            rrect(px, s, s, x, y, x+cell, y+cell, cell*0.26,
                  ON if (r_,c) in FILLED else OFF)
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", s, s, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(d, exist_ok=True)
for name, size in [("icon-192.png",192), ("icon-512.png",512), ("apple-touch-icon.png",180), ("favicon-32.png",32)]:
    open(os.path.join(d, name), "wb").write(render(size)); print(name)

# 店長用は地を紺にして見分けられるようにする
BG = (0x1B, 0x2C, 0x40)
ON = (0xF4, 0xEC, 0xDC)
OFF = (0x44, 0x53, 0x66)
BAR = (0xE0, 0xA1, 0x64)
for name, size in [("admin-192.png",192), ("admin-512.png",512), ("admin-180.png",180)]:
    open(os.path.join(d, name), "wb").write(render(size)); print(name)
