"""依存ライブラリなしで十字架のGLB(glTF 2.0 バイナリ)を生成する。
AR動作テスト用のサンプルモデル。実際の商品ではMeshy/Tripo等で作ったGLBに差し替える。
"""
import json, struct

def box(cx, cy, cz, sx, sy, sz):
    """中心(cx,cy,cz)、サイズ(sx,sy,sz)の直方体。面ごとに頂点を複製してフラットな法線を持たせる"""
    hx, hy, hz = sx/2, sy/2, sz/2
    faces = [  # (法線, 4頂点)
        ((0,0,1),  [(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]),
        ((0,0,-1), [(hx,-hy,-hz),(-hx,-hy,-hz),(-hx,hy,-hz),(hx,hy,-hz)]),
        ((1,0,0),  [(hx,-hy,hz),(hx,-hy,-hz),(hx,hy,-hz),(hx,hy,hz)]),
        ((-1,0,0), [(-hx,-hy,-hz),(-hx,-hy,hz),(-hx,hy,hz),(-hx,hy,-hz)]),
        ((0,1,0),  [(-hx,hy,hz),(hx,hy,hz),(hx,hy,-hz),(-hx,hy,-hz)]),
        ((0,-1,0), [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,-hy,hz),(-hx,-hy,hz)]),
    ]
    pos, nrm, idx = [], [], []
    for n, quad in faces:
        base = len(pos)
        for x, y, z in quad:
            pos.append((x+cx, y+cy, z+cz)); nrm.append(n)
        idx += [base, base+1, base+2, base, base+2, base+3]
    return pos, nrm, idx

def build():
    pos, nrm, idx = [], [], []
    for b in [box(0, 0.30, 0, 0.08, 0.60, 0.08),   # 縦棒
              box(0, 0.42, 0, 0.36, 0.08, 0.08),   # 横棒
              box(0, 0.01, 0, 0.30, 0.02, 0.30)]:  # 台座
        p, n, i = b
        off = len(pos)
        pos += p; nrm += n; idx += [j+off for j in i]

    pbuf = b''.join(struct.pack('<3f', *v) for v in pos)
    nbuf = b''.join(struct.pack('<3f', *v) for v in nrm)
    ibuf = b''.join(struct.pack('<H', i) for i in idx)
    while len(ibuf) % 4: ibuf += b'\0'
    bin_blob = pbuf + nbuf + ibuf
    mins = [min(v[k] for v in pos) for k in range(3)]
    maxs = [max(v[k] for v in pos) for k in range(3)]

    gltf = {
        "asset": {"version": "2.0", "generator": "mikotoba-ar"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "cross"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}]}],
        "materials": [{"name": "gold", "pbrMetallicRoughness": {
            "baseColorFactor": [0.95, 0.78, 0.35, 1.0], "metallicFactor": 0.9, "roughnessFactor": 0.35}}],
        "buffers": [{"byteLength": len(bin_blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pbuf), "target": 34962},
            {"buffer": 0, "byteOffset": len(pbuf), "byteLength": len(nbuf), "target": 34962},
            {"buffer": 0, "byteOffset": len(pbuf)+len(nbuf), "byteLength": len(ibuf), "target": 34963},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3", "min": mins, "max": maxs},
            {"bufferView": 1, "componentType": 5126, "count": len(nrm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5123, "count": len(idx), "type": "SCALAR"},
        ],
    }
    jbytes = json.dumps(gltf, separators=(',', ':')).encode()
    while len(jbytes) % 4: jbytes += b' '
    total = 12 + 8 + len(jbytes) + 8 + len(bin_blob)
    out = struct.pack('<III', 0x46546C67, 2, total)
    out += struct.pack('<II', len(jbytes), 0x4E4F534A) + jbytes
    out += struct.pack('<II', len(bin_blob), 0x004E4942) + bin_blob
    return out

if __name__ == "__main__":
    data = build()
    with open("models/cross.glb", "wb") as f: f.write(data)
    print(f"models/cross.glb を書き出しました ({len(data)} bytes)")
