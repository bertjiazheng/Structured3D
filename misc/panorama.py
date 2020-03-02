"""
Copy from https://github.com/sunset1995/pytorch-layoutnet/blob/master/pano.py
"""
import numpy as np
import numpy.matlib as matlib


def xyz_2_coorxy(xs, ys, zs, H=512, W=1024):
    us = np.arctan2(xs, ys)
    vs = -np.arctan(zs / np.sqrt(xs**2 + ys**2))
    coorx = (us / (2 * np.pi) + 0.5) * W
    coory = (vs / np.pi + 0.5) * H
    return coorx, coory


def coords2uv(coords, width, height):
    """
    Image coordinates (xy) to uv
    """
    middleX = width / 2 + 0.5
    middleY = height / 2 + 0.5
    uv = np.hstack([
        (coords[:, [0]] - middleX) / width * 2 * np.pi,
        -(coords[:, [1]] - middleY) / height * np.pi])
    return uv


def uv2xyzN(uv, planeID=1):
    ID1 = (int(planeID) - 1 + 0) % 3
    ID2 = (int(planeID) - 1 + 1) % 3
    ID3 = (int(planeID) - 1 + 2) % 3
    xyz = np.zeros((uv.shape[0], 3))
    xyz[:, ID1] = np.cos(uv[:, 1]) * np.sin(uv[:, 0])
    xyz[:, ID2] = np.cos(uv[:, 1]) * np.cos(uv[:, 0])
    xyz[:, ID3] = np.sin(uv[:, 1])
    return xyz


def uv2xyzN_vec(uv, planeID):
    """
    vectorization version of uv2xyzN
    @uv       N x 2
    @planeID  N
    """
    assert (planeID.astype(int) != planeID).sum() == 0
    planeID = planeID.astype(int)
    ID1 = (planeID - 1 + 0) % 3
    ID2 = (planeID - 1 + 1) % 3
    ID3 = (planeID - 1 + 2) % 3
    ID = np.arange(len(uv))
    xyz = np.zeros((len(uv), 3))
    xyz[ID, ID1] = np.cos(uv[:, 1]) * np.sin(uv[:, 0])
    xyz[ID, ID2] = np.cos(uv[:, 1]) * np.cos(uv[:, 0])
    xyz[ID, ID3] = np.sin(uv[:, 1])
    return xyz


def xyz2uvN(xyz, planeID=1):
    ID1 = (int(planeID) - 1 + 0) % 3
    ID2 = (int(planeID) - 1 + 1) % 3
    ID3 = (int(planeID) - 1 + 2) % 3
    normXY = np.sqrt(xyz[:, [ID1]] ** 2 + xyz[:, [ID2]] ** 2)
    normXY[normXY < 0.000001] = 0.000001
    normXYZ = np.sqrt(xyz[:, [ID1]] ** 2 + xyz[:, [ID2]] ** 2 + xyz[:, [ID3]] ** 2)
    v = np.arcsin(xyz[:, [ID3]] / normXYZ)
    u = np.arcsin(xyz[:, [ID1]] / normXY)
    valid = (xyz[:, [ID2]] < 0) & (u >= 0)
    u[valid] = np.pi - u[valid]
    valid = (xyz[:, [ID2]] < 0) & (u <= 0)
    u[valid] = -np.pi - u[valid]
    uv = np.hstack([u, v])
    uv[np.isnan(uv[:, 0]), 0] = 0
    return uv


def computeUVN(n, in_, planeID):
    """
    compute v given u and normal.
    """
    if planeID == 2:
        n = np.array([n[1], n[2], n[0]])
    elif planeID == 3:
        n = np.array([n[2], n[0], n[1]])
    bc = n[0] * np.sin(in_) + n[1] * np.cos(in_)
    bs = n[2]
    out = np.arctan(-bc / (bs + 1e-9))
    return out


def computeUVN_vec(n, in_, planeID):
    """
    vectorization version of computeUVN
    @n         N x 3
    @in_      MN x 1
    @planeID   N
    """
    n = n.copy()
    if (planeID == 2).sum():
        n[planeID == 2] = np.roll(n[planeID == 2], 2, axis=1)
    if (planeID == 3).sum():
        n[planeID == 3] = np.roll(n[planeID == 3], 1, axis=1)
    n = np.repeat(n, in_.shape[0] // n.shape[0], axis=0)
    assert n.shape[0] == in_.shape[0]
    bc = n[:, [0]] * np.sin(in_) + n[:, [1]] * np.cos(in_)
    bs = n[:, [2]]
    out = np.arctan(-bc / (bs + 1e-9))
    return out


def lineFromTwoPoint(pt1, pt2):
    """
    Generate line segment based on two points on panorama
    pt1, pt2: two points on panorama
    line:
        1~3-th dim: normal of the line
        4-th dim: the projection dimension ID
        5~6-th dim: the u of line segment endpoints in projection plane
    """
    numLine = pt1.shape[0]
    lines = np.zeros((numLine, 6))
    n = np.cross(pt1, pt2)
    n = n / (matlib.repmat(np.sqrt(np.sum(n ** 2, 1, keepdims=True)), 1, 3) + 1e-9)
    lines[:, 0:3] = n

    areaXY = np.abs(np.sum(n * matlib.repmat([0, 0, 1], numLine, 1), 1, keepdims=True))
    areaYZ = np.abs(np.sum(n * matlib.repmat([1, 0, 0], numLine, 1), 1, keepdims=True))
    areaZX = np.abs(np.sum(n * matlib.repmat([0, 1, 0], numLine, 1), 1, keepdims=True))
    planeIDs = np.argmax(np.hstack([areaXY, areaYZ, areaZX]), axis=1) + 1
    lines[:, 3] = planeIDs

    for i in range(numLine):
        uv = xyz2uvN(np.vstack([pt1[i, :], pt2[i, :]]), lines[i, 3])
        umax = uv[:, 0].max() + np.pi
        umin = uv[:, 0].min() + np.pi
        if umax - umin > np.pi:
            lines[i, 4:6] = np.array([umax, umin]) / 2 / np.pi
        else:
            lines[i, 4:6] = np.array([umin, umax]) / 2 / np.pi

    return lines


def lineIdxFromCors(cor_all, im_w, im_h):
    assert len(cor_all) % 2 == 0
    uv = coords2uv(cor_all, im_w, im_h)
    xyz = uv2xyzN(uv)
    lines = lineFromTwoPoint(xyz[0::2], xyz[1::2])
    num_sample = max(im_h, im_w)

    cs, rs = [], []
    for i in range(lines.shape[0]):
        n = lines[i, 0:3]
        sid = lines[i, 4] * 2 * np.pi
        eid = lines[i, 5] * 2 * np.pi
        if eid < sid:
            x = np.linspace(sid, eid + 2 * np.pi, num_sample)
            x = x % (2 * np.pi)
        else:
            x = np.linspace(sid, eid, num_sample)

        u = -np.pi + x.reshape(-1, 1)
        v = computeUVN(n, u, lines[i, 3])
        xyz = uv2xyzN(np.hstack([u, v]), lines[i, 3])
        uv = xyz2uvN(xyz, 1)

        r = np.minimum(np.floor((uv[:, 0] + np.pi) / (2 * np.pi) * im_w) + 1,
                       im_w).astype(np.int32)
        c = np.minimum(np.floor((np.pi / 2 - uv[:, 1]) / np.pi * im_h) + 1,
                       im_h).astype(np.int32)
        cs.extend(r - 1)
        rs.extend(c - 1)
    return rs, cs


def draw_boundary_from_cor_id(cor_id, img_src):
    im_h, im_w = img_src.shape[:2]
    cor_all = [cor_id]
    for i in range(len(cor_id)):
        cor_all.append(cor_id[i, :])
        cor_all.append(cor_id[(i+2) % len(cor_id), :])
    cor_all = np.vstack(cor_all)

    rs, cs = lineIdxFromCors(cor_all, im_w, im_h)
    rs = np.array(rs)
    cs = np.array(cs)

    panoEdgeC = img_src.astype(np.uint8)
    for dx, dy in [[-1, 0], [1, 0], [0, 0], [0, 1], [0, -1]]:
        panoEdgeC[np.clip(rs + dx, 0, im_h - 1), np.clip(cs + dy, 0, im_w - 1), 0] = 0
        panoEdgeC[np.clip(rs + dx, 0, im_h - 1), np.clip(cs + dy, 0, im_w - 1), 1] = 0
        panoEdgeC[np.clip(rs + dx, 0, im_h - 1), np.clip(cs + dy, 0, im_w - 1), 2] = 255

    return panoEdgeC


def coorx2u(x, w=1024):
    return ((x + 0.5) / w - 0.5) * 2 * np.pi


def coory2v(y, h=512):
    return ((y + 0.5) / h - 0.5) * np.pi


def u2coorx(u, w=1024):
    return (u / (2 * np.pi) + 0.5) * w - 0.5


def v2coory(v, h=512):
    return (v / np.pi + 0.5) * h - 0.5


def uv2xy(u, v, z=-50):
    c = z / np.tan(v)
    x = c * np.cos(u)
    y = c * np.sin(u)
    return x, y


def pano_connect_points(p1, p2, z=-50, w=1024, h=512):
    u1 = coorx2u(p1[0], w)
    v1 = coory2v(p1[1], h)
    u2 = coorx2u(p2[0], w)
    v2 = coory2v(p2[1], h)

    x1, y1 = uv2xy(u1, v1, z)
    x2, y2 = uv2xy(u2, v2, z)

    if abs(p1[0] - p2[0]) < w / 2:
        pstart = np.ceil(min(p1[0], p2[0]))
        pend = np.floor(max(p1[0], p2[0]))
    else:
        pstart = np.ceil(max(p1[0], p2[0]))
        pend = np.floor(min(p1[0], p2[0]) + w)
    coorxs = (np.arange(pstart, pend + 1) % w).astype(np.float64)
    vx = x2 - x1
    vy = y2 - y1
    us = coorx2u(coorxs, w)
    ps = (np.tan(us) * x1 - y1) / (vy - np.tan(us) * vx)
    cs = np.sqrt((x1 + ps * vx) ** 2 + (y1 + ps * vy) ** 2)
    vs = np.arctan2(z, cs)
    coorys = v2coory(vs)

    return np.stack([coorxs, coorys], axis=-1)
