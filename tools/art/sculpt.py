"""Tiny 3D-sculpt -> pixel-art renderer (dev tool, not shipped with the game).

A scene is a set of groups; each group is a sequence of primitives (sphere, ellipsoid, round cone,
torus) that are added with smooth-min (clay-like blending) or carved with smooth subtraction.
Orthographic camera looking down -z: x right, y down (image coordinates), z toward the viewer.

Lighting (key light, soft cast shadows, ambient occlusion, rim, wet specular) is quantized onto
hand-picked colour ramps, then pixel-art post: supersampled "mode" downscale, coloured outlines,
depth-edge lines and orphan-pixel cleanup. Hand-placed details are painted on the result.
"""
import numpy as np
from PIL import Image


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], dtype=np.uint8)


def rotm(rx=0.0, ry=0.0, rz=0.0):
    """Local->world rotation (degrees). With y down, +rz turns clockwise on screen."""
    rx, ry, rz = np.radians([rx, ry, rz])
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


# ----------------------------------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------------------------------

class Sphere:
    def __init__(self, c, r):
        self.c = np.array(c, float)
        self.r = float(r)
        self.bc, self.br = self.c, self.r

    def sdf(self, P):
        q = P - self.c
        return np.sqrt((q * q).sum(1)) - self.r


class Ellipsoid:
    def __init__(self, c, r, rot=(0, 0, 0)):
        self.c = np.array(c, float)
        self.r = np.array(r, float)
        self.R = rotm(*rot)
        self.bc, self.br = self.c, float(self.r.max())

    def sdf(self, P):
        q = (P - self.c) @ self.R
        k0 = np.sqrt(((q / self.r) ** 2).sum(1))
        k1 = np.sqrt(((q / (self.r * self.r)) ** 2).sum(1))
        return np.where(k1 > 1e-9, k0 * (k0 - 1.0) / np.maximum(k1, 1e-9), -self.r.min())


class Cone:
    """Round cone / tapered capsule from a (radius ra) to b (radius rb). (iq's exact SDF)"""

    def __init__(self, a, b, ra, rb):
        self.a = np.array(a, float)
        self.b = np.array(b, float)
        self.ra, self.rb = float(ra), float(rb)
        ba = self.b - self.a
        self.ba = ba
        self.l2 = float(ba @ ba)
        self.rr = self.ra - self.rb
        self.a2 = self.l2 - self.rr * self.rr
        self.il2 = 1.0 / self.l2
        self.bc = (self.a + self.b) * 0.5
        self.br = np.sqrt(self.l2) * 0.5 + max(self.ra, self.rb)

    def sdf(self, P):
        pa = P - self.a
        y = pa @ self.ba
        z = y - self.l2
        xv = pa * self.l2 - np.outer(y, self.ba)
        x2 = (xv * xv).sum(1)
        y2 = y * y * self.l2
        z2 = z * z * self.l2
        k = np.sign(self.rr) * self.rr * self.rr * x2
        d_b = np.sqrt(x2 + z2) * self.il2 - self.rb
        d_a = np.sqrt(x2 + y2) * self.il2 - self.ra
        d_m = (np.sqrt(np.maximum(x2 * self.a2 * self.il2, 0.0)) + y * self.rr) * self.il2 - self.ra
        return np.where(np.sign(z) * self.a2 * z2 > k, d_b, np.where(np.sign(y) * self.a2 * y2 < k, d_a, d_m))


class Torus:
    def __init__(self, c, axis, R, r):
        self.c = np.array(c, float)
        n = np.array(axis, float)
        self.n = n / np.linalg.norm(n)
        self.R, self.r = float(R), float(r)
        self.bc, self.br = self.c, self.R + self.r

    def sdf(self, P):
        q = P - self.c
        h = q @ self.n
        rad = np.sqrt(np.maximum((q * q).sum(1) - h * h, 0.0))
        return np.sqrt((rad - self.R) ** 2 + h * h) - self.r


def smin_m(d1, m1, d2, m2, k):
    if k <= 0:
        sel = d2 < d1
        return np.where(sel, d2, d1), np.where(sel, m2, m1)
    h = np.clip(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0)
    d = d2 * (1.0 - h) + d1 * h - k * h * (1.0 - h)
    return d, np.where(h > 0.5, m1, m2)


def ssub_m(d, m, dc, mc, k):
    """Carve cutter dc out of d. Carved surface gets material mc (or keeps m if mc is None)."""
    if k <= 0:
        cut = -dc > d
        dn = np.maximum(d, -dc)
    else:
        h = np.clip(0.5 - 0.5 * (d + dc) / k, 0.0, 1.0)
        dn = d * (1.0 - h) + (-dc) * h + k * h * (1.0 - h)
        cut = h > 0.5
    if mc is not None:
        m = np.where(cut, mc, m)
    return dn, m


# ----------------------------------------------------------------------------------------------
# materials / scene
# ----------------------------------------------------------------------------------------------

class Mat:
    def __init__(self, idx, name, ramp, outline, spec=None, shin=30.0, spec_thr=0.45, line=None):
        self.idx, self.name = idx, name
        self.ramp = [hexc(c) for c in ramp]       # 5 colours, dark -> light
        self.outline = hexc(outline)
        self.line = hexc(line) if line else self.outline
        self.spec = hexc(spec) if spec else None
        self.shin, self.spec_thr = shin, spec_thr


class Group:
    def __init__(self, k):
        self.k = k
        self.ops = []

    def eval(self, P):
        d = None
        m = None
        for prim, op, k, mat in self.ops:
            di = prim.sdf(P)
            if op == "add":
                if d is None:
                    d, m = di, np.full(len(P), mat)
                else:
                    d, m = smin_m(d, m, di, mat, k)
            elif d is not None:     # a carve with nothing before it has nothing to cut
                d, m = ssub_m(d, m, di, mat, k)
        return d, m


class Scene:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.mats = []
        self.groups = []
        self.cur = None
        self.L = np.array([-0.55, -0.75, 0.62])
        self.L /= np.linalg.norm(self.L)
        self.rim_dir = np.array([1.0, 0.15])
        self.rim_dir /= np.linalg.norm(self.rim_dir)
        self.rim_col = None
        self.ambient = 0.26
        self.thresholds = [0.22, 0.38, 0.55, 0.75]
        self.edge_thr = 3.0
        self.rim3d = False
        self.rim_px = True

    # --- authoring -----------------------------------------------------------------------------
    def mat(self, name, ramp, outline, **kw):
        m = Mat(len(self.mats), name, ramp, outline, **kw)
        self.mats.append(m)
        return m.idx

    def group(self, k=0.0):
        self.cur = Group(k)
        self.groups.append(self.cur)
        return self.cur

    def _add(self, prim, mat, k, op="add"):
        if self.cur is None:
            self.group()
        self.cur.ops.append((prim, op, k, mat))

    def sphere(self, c, r, mat, k=0.0):
        self._add(Sphere(c, r), mat, k)

    def ell(self, c, r, mat, k=0.0, rot=(0, 0, 0)):
        self._add(Ellipsoid(c, r, rot), mat, k)

    def cone(self, a, b, ra, rb, mat, k=0.0):
        self._add(Cone(a, b, ra, rb), mat, k)

    def chain(self, pts, radii, mat, k=0.0):
        for i in range(len(pts) - 1):
            self.cone(pts[i], pts[i + 1], radii[i], radii[i + 1], mat, k)

    def torus(self, c, axis, R, r, mat, k=0.0):
        self._add(Torus(c, axis, R, r), mat, k)

    def carve_sphere(self, c, r, k=0.0, mat=None):
        self._add(Sphere(c, r), mat, k, op="sub")

    def carve_ell(self, c, r, k=0.0, mat=None, rot=(0, 0, 0)):
        self._add(Ellipsoid(c, r, rot), mat, k, op="sub")

    # --- evaluation ----------------------------------------------------------------------------
    def eval(self, P):
        d = None
        m = None
        for g in self.groups:
            dg, mg = g.eval(P)
            if dg is None:          # a group that ended up with no shapes
                continue
            if d is None:
                d, m = dg, mg
            else:
                d, m = smin_m(d, m, dg, mg, g.k)
        return d, m

    def _prims(self):
        for g in self.groups:
            for prim, op, k, mat in g.ops:
                if op == "add":
                    yield prim, k + g.k

    def normals(self, P, e=0.3):
        out = np.zeros_like(P)
        for i in range(3):
            o = np.zeros(3)
            o[i] = e
            out[:, i] = self.eval(P + o)[0] - self.eval(P - o)[0]
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)

    def render(self, ss=3):
        W, H = self.w * ss, self.h * ss
        ys, xs = np.mgrid[0:H, 0:W]
        ox = (xs.ravel() + 0.5) / ss
        oy = (ys.ravel() + 0.5) / ss
        N = len(ox)

        # rays that can possibly hit something (2D bounding circles)
        alive = np.zeros(N, bool)
        zmax, zmin = -1e9, 1e9
        for prim, kk in self._prims():
            rad = prim.br + kk + 1.0
            alive |= (ox - prim.bc[0]) ** 2 + (oy - prim.bc[1]) ** 2 < rad * rad
            zmax = max(zmax, prim.bc[2] + rad)
            zmin = min(zmin, prim.bc[2] - rad)

        t = np.zeros(N)
        hit = np.zeros(N, bool)
        for _ in range(220):
            idx = np.nonzero(alive)[0]
            if len(idx) == 0:
                break
            P = np.stack([ox[idx], oy[idx], zmax - t[idx]], 1)
            d, _ = self.eval(P)
            done = d < 0.02
            hit[idx[done]] = True
            alive[idx[done]] = False
            t[idx[~done]] += np.maximum(d[~done] * 0.8, 0.02)
            gone = (zmax - t[idx]) < zmin
            alive[idx[gone & ~done]] = False

        hidx = np.nonzero(hit)[0]
        P = np.stack([ox[hidx], oy[hidx], zmax - t[hidx]], 1)
        _, mat = self.eval(P)
        n = self.normals(P)

        # soft shadow toward the key light
        sh = np.ones(len(P))
        tt = np.full(len(P), 0.6)
        base = P + n * 0.4
        for _ in range(36):
            d, _ = self.eval(base + self.L[None, :] * tt[:, None])
            sh = np.minimum(sh, 7.0 * d / tt)
            tt += np.clip(d, 0.3, 3.0)
        sh = np.clip(sh, 0.0, 1.0)

        # ambient occlusion
        occ = np.zeros(len(P))
        sca = 1.0
        for i in range(1, 6):
            hh = 0.9 * i
            d, _ = self.eval(P + n * hh)
            occ += (hh - d) * sca
            sca *= 0.75
        ao = np.clip(1.0 - 0.18 * occ, 0.0, 1.0)

        diff = np.clip(n @ self.L, 0.0, 1.0)
        v = self.ambient * ao + (1.0 - self.ambient) * diff * sh
        v *= 0.75 + 0.25 * ao
        idx = np.searchsorted(self.thresholds, v)

        # wet specular
        Hh = self.L + np.array([0.0, 0.0, 1.0])
        Hh /= np.linalg.norm(Hh)
        spec = np.clip(n @ Hh, 0.0, 1.0)
        for m in self.mats:
            if m.spec is None:
                continue
            sel = (mat == m.idx) & (spec ** m.shin > m.spec_thr) & (sh > 0.6)
            idx[sel] = 5

        # rim light from behind-right, only in the dark tones
        nxy = n[:, :2] / np.maximum(np.linalg.norm(n[:, :2], axis=1, keepdims=True), 1e-9)
        rim = (1.0 - np.clip(n[:, 2], 0.0, 1.0)) * np.clip(nxy @ self.rim_dir, 0.0, 1.0)
        if self.rim3d:
            idx[(rim > 0.62) & (idx <= 1)] = 6

        code = np.full(N, -1, np.int32)
        code[hidx] = mat * 8 + idx
        z = np.full(N, -1e9)
        z[hidx] = P[:, 2]

        # supersampled -> 1x by mode
        code = code.reshape(self.h, ss, self.w, ss).transpose(0, 2, 1, 3).reshape(self.h, self.w, ss * ss)
        z = z.reshape(self.h, ss, self.w, ss).transpose(0, 2, 1, 3).reshape(self.h, self.w, ss * ss)
        eq = code[:, :, :, None] == code[:, :, None, :]
        cnt = eq.sum(3)
        cnt = np.where(code < 0, cnt - 0.5, cnt)   # ties break toward the figure
        best = np.take_along_axis(code, cnt.argmax(2)[:, :, None], 2)[:, :, 0]
        bgc = (code < 0).sum(2)
        best[bgc * 2 > ss * ss] = -1
        depth = z.max(2)
        return Render(self, best, depth)


class Render:
    def __init__(self, scene, code, depth):
        self.scene = scene
        self.code = code.copy()
        self.depth = depth
        self.h, self.w = code.shape
        self.over = {}      # (x, y) -> rgba painted on top

    @property
    def mat(self):
        return np.where(self.code >= 0, self.code // 8, -1)

    def cleanup(self):
        c = self.code
        out = c.copy()
        for y in range(1, self.h - 1):
            for x in range(1, self.w - 1):
                v = c[y, x]
                if v < 0:
                    continue
                nb = [c[y - 1, x], c[y + 1, x], c[y, x - 1], c[y, x + 1]]
                if nb[0] == nb[1] == nb[2] == nb[3] and nb[0] != v and nb[0] >= 0:
                    out[y, x] = nb[0]
        self.code = out

    def to_rgba(self, outline=True, selout=False):
        S = self.scene
        img = np.zeros((self.h, self.w, 4), np.uint8)
        mat = self.mat
        for y in range(self.h):
            for x in range(self.w):
                c = self.code[y, x]
                if c < 0:
                    continue
                m = S.mats[c // 8]
                i = c % 8
                if i == 5:
                    img[y, x] = m.spec
                elif i == 6:
                    img[y, x] = S.rim_col if S.rim_col is not None else m.ramp[2]
                else:
                    img[y, x] = m.ramp[i]
        # depth-edge lines: the pixel behind gets its material's line colour
        d = self.depth
        for y in range(self.h):
            for x in range(self.w):
                if self.code[y, x] < 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and self.code[yy, xx] >= 0:
                        if d[yy, xx] > d[y, x] + S.edge_thr:
                            img[y, x] = S.mats[mat[y, x]].line
                            break
        if S.rim_px and S.rim_col is not None:
            for y in range(self.h):
                for x in range(self.w - 1):
                    c = self.code[y, x]
                    if c >= 0 and self.code[y, x + 1] < 0 and c % 8 <= 2:
                        img[y, x] = S.rim_col
        for (x, y), col in self.over.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                img[y, x] = col
        if outline:
            solid = img[:, :, 3] > 0
            out = img.copy()
            for y in range(self.h):
                for x in range(self.w):
                    if solid[y, x]:
                        continue
                    best = None
                    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < self.w and 0 <= yy < self.h and solid[yy, xx]:
                            mm = mat[yy, xx]
                            if mm < 0:
                                best = hexc("#0c0810")
                                continue
                            m = S.mats[mm]
                            ci = self.code[yy, xx] % 8
                            best = m.ramp[0] if (selout and ci >= 3) else m.outline
                    if best is not None:
                        out[y, x] = best
            img = out
        return img

    # --- hand-placed details ---------------------------------------------------------------------
    def px(self, x, y, col):
        self.over[(int(x), int(y))] = hexc(col) if isinstance(col, str) else col

    def pxs(self, pts, col):
        for x, y in pts:
            self.px(x, y, col)

    def line(self, a, b, col):
        x0, y0 = a
        x1, y1 = b
        n = int(max(abs(x1 - x0), abs(y1 - y0)))
        for i in range(n + 1):
            t = i / max(n, 1)
            self.px(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), col)

    def poly(self, pts, col):
        for i in range(len(pts) - 1):
            self.line(pts[i], pts[i + 1], col)

    def on(self, x, y, mat_idx):
        return 0 <= x < self.w and 0 <= y < self.h and self.mat[y, x] == mat_idx


def save(img, path, scale=1):
    im = Image.fromarray(img, "RGBA")
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
