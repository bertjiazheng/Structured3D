import os
import json
import argparse

import cv2
import open3d
import numpy as np
from panda3d.core import Triangulator

from misc.panorama import xyz_2_coorxy
from visualize_3d import convert_lines_to_vertices


def E2P(image, corner_i, corner_j, wall_height, camera, resolution=512, is_wall=True):
    """convert panorama to persepctive image
    """
    corner_i = corner_i - camera
    corner_j = corner_j - camera

    if is_wall:
        xs = np.linspace(corner_i[0], corner_j[0], resolution)[None].repeat(resolution, 0)
        ys = np.linspace(corner_i[1], corner_j[1], resolution)[None].repeat(resolution, 0)
        zs = np.linspace(-camera[-1], wall_height - camera[-1], resolution)[:, None].repeat(resolution, 1)
    else:
        xs = np.linspace(corner_i[0], corner_j[0], resolution)[None].repeat(resolution, 0)
        ys = np.linspace(corner_i[1], corner_j[1], resolution)[:, None].repeat(resolution, 1)
        zs = np.zeros_like(xs) + wall_height - camera[-1]

    coorx, coory = xyz_2_coorxy(xs, ys, zs)

    persp = cv2.remap(image, coorx.astype(np.float32), coory.astype(np.float32), 
                      cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)

    return persp


def create_plane_mesh(vertices, vertices_floor, textures, texture_floor, texture_ceiling, delta_height):
    triangles = []
    triangle_uvs = []

    # the number of vertical walls (ignore ceiling and floor)
    num_walls = len(vertices)

    # 1. vertical wall (always rectangle)
    num_vertices = 0
    for i in range(len(vertices)):
        # hardcode mesh for each wall
        triangle = np.array([[0, 2, 1], [2, 0, 3]])
        triangles.append(triangle + num_vertices)
        num_vertices += 4

        triangle_uv = np.array(
            [
                [i / (num_walls + 2), 0], 
                [i / (num_walls + 2), 1], 
                [(i+1) / (num_walls + 2), 1], 
                [(i+1) / (num_walls + 2), 0]
            ],
            dtype=np.float32
        )
        triangle_uvs.append(triangle_uv)

    # 2. floor and ceiling
    # Since the floor and ceiling may not be a rectangle, 
    # we first triangulate this polygon.
    tri = Triangulator()
    for i in range(len(vertices_floor)):
        tri.add_vertex(vertices_floor[i, 0], vertices_floor[i, 1])

    for i in range(len(vertices_floor)):
        tri.add_polygon_vertex(i)

    tri.triangulate()

    triangle = []
    for i in range(tri.getNumTriangles()):
        triangle.append([tri.get_triangle_v0(i), tri.get_triangle_v1(i), tri.get_triangle_v2(i)])
    triangle = np.array(triangle)

    # add triangles for floor and ceiling
    triangles.append(triangle + num_vertices)
    num_vertices += len(np.unique(triangle))
    triangles.append(triangle + num_vertices)

    # texture for floor and ceiling
    vertices_floor_min = np.min(vertices_floor[:, :2], axis=0)
    vertices_floor_max = np.max(vertices_floor[:, :2], axis=0)
    
    # normalize to [0, 1]
    triangle_uv = (vertices_floor[:, :2] - vertices_floor_min) / (vertices_floor_max - vertices_floor_min)
    triangle_uv[:, 0] = (triangle_uv[:, 0] + num_walls) / (num_walls + 2) 

    triangle_uvs.append(triangle_uv)

    # normalize to [0, 1]
    triangle_uv = (vertices_floor[:, :2] - vertices_floor_min) / (vertices_floor_max - vertices_floor_min)
    triangle_uv[:, 0] = (triangle_uv[:, 0] + num_walls + 1) / (num_walls + 2)

    triangle_uvs.append(triangle_uv)

    # 3. Merge wall, floor, and ceiling
    vertices.append(vertices_floor)
    vertices.append(vertices_floor + delta_height)
    vertices = np.concatenate(vertices, axis=0)

    triangles = np.concatenate(triangles, axis=0)

    textures.append(texture_floor)
    textures.append(texture_ceiling)
    textures = np.concatenate(textures, axis=1)

    triangle_uvs = np.concatenate(triangle_uvs, axis=0)

    mesh = open3d.geometry.TriangleMesh(
        vertices=open3d.utility.Vector3dVector(vertices),
        triangles=open3d.utility.Vector3iVector(triangles)
    )
    mesh.compute_vertex_normals()

    mesh.texture = open3d.geometry.Image(textures)
    mesh.triangle_uvs = np.array(triangle_uvs[triangles.reshape(-1), :], dtype=np.float64)
    return mesh


def visualize_mesh(args):
    """visualize as water-tight mesh
    """
    
    image = cv2.imread(os.path.join(args.path, f"scene_{args.scene:05d}", "2D_rendering", 
                                    str(args.room), "panorama/full/rgb_rawlight.png"))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # load room annotations
    with open(os.path.join(args.path, f"scene_{args.scene:05d}" , "annotation_3d.json")) as f:
        annos = json.load(f)

    # load camera info
    camera_center = np.loadtxt(os.path.join(args.path, f"scene_{args.scene:05d}", "2D_rendering", 
                                            str(args.room), "panorama", "camera_xyz.txt"))

    # parse corners
    junctions = np.array([item['coordinate'] for item in annos['junctions']])
    lines_holes = []
    for semantic in annos['semantics']:
        if semantic['type'] in ['window', 'door']:
            for planeID in semantic['planeID']:
                lines_holes.extend(np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist())

    lines_holes = np.unique(lines_holes)
    _, vertices_holes = np.where(np.array(annos['lineJunctionMatrix'])[lines_holes])
    vertices_holes = np.unique(vertices_holes)

    # load polygons
    walls = dict()
    for semantic in annos['semantics']:
        if semantic['ID'] != int(args.room):
            continue
        for planeID in semantic['planeID']:
            plane_anno = annos['planes'][planeID]

            if plane_anno['type'] != 'wall':
                lineIDs = np.where(np.array(annos['planeLineMatrix'][planeID]))[0]
                lineIDs = np.setdiff1d(lineIDs, lines_holes)
                junction_pairs = [np.where(np.array(annos['lineJunctionMatrix'][lineID]))[0].tolist() for lineID in lineIDs]
                wall = convert_lines_to_vertices(junction_pairs)
                walls[plane_anno['type']] = wall[0]

    # we assume that zs of floor equals 0, then the wall height is from the ceiling
    wall_height = np.mean(junctions[walls['ceiling']], axis=0)[-1]
    delta_height = np.array([0, 0, wall_height])

    # list of corner index
    wall_floor = walls['floor']

    corners = []    # 3D coordinate for each wall
    textures = []   # texture for each wall

    # wall
    for i, j in zip(wall_floor, np.roll(wall_floor, shift=-1)):
        corner_i, corner_j = junctions[i], junctions[j]

        texture = E2P(image, corner_i, corner_j, wall_height, camera_center)

        corner = np.array([corner_i, corner_i + delta_height, corner_j + delta_height, corner_j])

        corners.append(corner)
        textures.append(texture)

    # floor and ceiling
    # the floor/ceiling texture is cropped by the maximum bounding box
    corner_floor = junctions[wall_floor]
    corner_min = np.min(corner_floor, axis=0)
    corner_max = np.max(corner_floor, axis=0)
    texture_floor = E2P(image, corner_min, corner_max, 0, camera_center, is_wall=False)
    texture_ceiling = E2P(image, corner_min, corner_max, wall_height, camera_center, is_wall=False)

    # create mesh
    mesh = create_plane_mesh(corners, corner_floor, textures, texture_floor, texture_ceiling, delta_height)

    # visualize mesh
    open3d.visualization.draw_geometries([mesh])


def parse_args():
    parser = argparse.ArgumentParser(description="Structured3D 2D Layout Visualization")
    parser.add_argument("--path", required=True,
                        help="dataset path", metavar="DIR")
    parser.add_argument("--scene", required=True,
                        help="scene id", type=int)
    parser.add_argument("--room", required=True,
                        help="room id", type=int)
    return parser.parse_args()


def main():
    args = parse_args()

    visualize_mesh(args)


if __name__ == "__main__":
    main()
