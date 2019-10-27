import os
import json
import argparse

import open3d
import pymesh
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from descartes.patch import PolygonPatch

from misc.figures import plot_coords
from misc.colors import colormap_255, semantics_cmap


def visualize_wireframe(annos):
    """visualize wireframe
    """
    colormap = np.array(colormap_255) / 255

    junctions = np.array([item['coordinate'] for item in annos['junctions']])
    _, junction_pairs = np.where(np.array(annos['lineJunctionMatrix']))
    junction_pairs = junction_pairs.reshape(-1, 2)

    # extract hole lines
    lines_holes = []
    for semantic in annos['semantics']:
        if semantic['type'] in ['window', 'door']:
            for planeID in semantic['planeID']:
                lines_holes.extend(np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist())
    lines_holes = np.unique(lines_holes)

    # extract cuboid lines
    cuboid_lines = []
    for cuboid in annos['cuboids']:
        for planeID in cuboid['planeID']:
            cuboid_lineID = np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist()
            cuboid_lines.extend(cuboid_lineID)
    cuboid_lines = np.unique(cuboid_lines)
    cuboid_lines = np.setdiff1d(cuboid_lines, lines_holes)

    # visualize junctions
    connected_junctions = junctions[np.unique(junction_pairs)]
    connected_colors = np.repeat(colormap[0].reshape(1, 3), len(connected_junctions), axis=0)

    junction_set = open3d.geometry.PointCloud()
    junction_set.points = open3d.utility.Vector3dVector(connected_junctions)
    junction_set.colors = open3d.utility.Vector3dVector(connected_colors)

    # visualize line segments
    line_colors = np.repeat(colormap[5].reshape(1, 3), len(junction_pairs), axis=0)

    # color holes
    if len(lines_holes) != 0:
        line_colors[lines_holes] = colormap[6]

    # color cuboids
    if len(cuboid_lines) != 0:
        line_colors[cuboid_lines] = colormap[2]

    line_set = open3d.geometry.LineSet()
    line_set.points = open3d.utility.Vector3dVector(junctions)
    line_set.lines = open3d.utility.Vector2iVector(junction_pairs)
    line_set.colors = open3d.utility.Vector3dVector(line_colors)

    open3d.visualization.draw_geometries([junction_set, line_set])


def project(x, meta):
    """ project 3D to 2D for polygon clipping
    """
    proj_axis = max(range(3), key=lambda i: abs(meta['normal'][i]))

    return tuple(c for i, c in enumerate(x) if i != proj_axis)


def project_inv(x, meta):
    """ recover 3D points from 2D
    """
    # Returns the vector w in the walls' plane such that project(w) equals x.
    proj_axis = max(range(3), key=lambda i: abs(meta['normal'][i]))

    w = list(x)
    w[proj_axis:proj_axis] = [0.0]
    c = -meta['offset']
    for i in range(3):
        c -= w[i] * meta['normal'][i]
    c /= meta['normal'][proj_axis]
    w[proj_axis] = c
    return tuple(w)


def triangulate(points):
    """ triangulate the plane for operation and visualization
    """
    num_points = len(points)
    indices = np.arange(num_points, dtype=np.int)
    segments = np.vstack((indices, np.roll(indices, -1))).T

    tri = pymesh.triangle()
    tri.points = np.array(points)

    tri.segments = segments
    tri.verbosity = 0
    tri.run()

    return tri.mesh


def clip_polygon(polygons, vertices_hole, junctions, meta):
    """ clip polygon the hole
    """
    if len(polygons) == 1:
        junctions = [junctions[vertex] for vertex in polygons[0]]
        mesh_wall = triangulate(junctions)

        vertices = np.array(mesh_wall.vertices)
        faces = np.array(mesh_wall.faces)

        return vertices, faces

    else:
        wall = []
        holes = []
        for polygon in polygons:
            if np.any(np.intersect1d(polygon, vertices_hole)):
                holes.append(polygon)
            else:
                wall.append(polygon)

        # extract junctions on this plane
        indices = []
        junctions_wall = []
        for plane in wall:
            for vertex in plane:
                indices.append(vertex)
                junctions_wall.append(junctions[vertex])

        junctions_holes = []
        for plane in holes:
            junctions_hole = []
            for vertex in plane:
                indices.append(vertex)
                junctions_hole.append(junctions[vertex])
            junctions_holes.append(junctions_hole)

        junctions_wall = [project(x, meta) for x in junctions_wall]
        junctions_holes = [[project(x, meta) for x in junctions_hole] for junctions_hole in junctions_holes]

        mesh_wall = triangulate(junctions_wall)

        for hole in junctions_holes:
            mesh_hole = triangulate(hole)
            mesh_wall = pymesh.boolean(mesh_wall, mesh_hole, 'difference')

        vertices = [project_inv(vertex, meta) for vertex in mesh_wall.vertices]

        return vertices, np.array(mesh_wall.faces)


def draw_geometries_with_back_face(geometries):
    vis = open3d.Visualizer()
    vis.create_window()
    render_option = vis.get_render_option()
    render_option.mesh_show_back_face = True
    for geometry in geometries:
        vis.add_geometry(geometry)
    vis.run()
    vis.destroy_window()


def convert_lines_to_vertices(lines):
    """convert line representation to polygon vertices
    """
    polygons = []
    lines = np.array(lines)

    polygon = None
    while len(lines) != 0:
        if polygon is None:
            polygon = lines[0].tolist()
            lines = np.delete(lines, 0, 0)

        lineID, juncID = np.where(lines == polygon[-1])
        vertex = lines[lineID[0], 1 - juncID[0]]
        lines = np.delete(lines, lineID, 0)

        if vertex in polygon:
            polygons.append(polygon)
            polygon = None
        else:
            polygon.append(vertex)

    return polygons


def visualize_plane(annos, args, eps=0.9):
    """visualize plane
    """
    colormap = np.array(colormap_255) / 255
    junctions = [item['coordinate'] for item in annos['junctions']]

    if args.color == 'manhattan':
        manhattan = dict()
        for planes in annos['manhattan']:
            for planeID in planes['planeID']:
                manhattan[planeID] = planes['ID']

    # extract hole vertices
    lines_holes = []
    for semantic in annos['semantics']:
        if semantic['type'] in ['window', 'door']:
            for planeID in semantic['planeID']:
                lines_holes.extend(np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist())

    lines_holes = np.unique(lines_holes)
    _, vertices_holes = np.where(np.array(annos['lineJunctionMatrix'])[lines_holes])
    vertices_holes = np.unique(vertices_holes)

    # load polygons
    polygons = []
    for semantic in annos['semantics']:
        for planeID in semantic['planeID']:
            plane_anno = annos['planes'][planeID]
            lineIDs = np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist()
            junction_pairs = [np.where(np.array(annos['lineJunctionMatrix'][lineID]))[0].tolist() for lineID in lineIDs]
            polygon = convert_lines_to_vertices(junction_pairs)
            vertices, faces = clip_polygon(polygon, vertices_holes, junctions, plane_anno)
            polygons.append([vertices, faces, planeID, plane_anno['normal'], plane_anno['type'], semantic['type']])

    plane_set = []
    for i, (vertices, faces, planeID, normal, plane_type, semantic_type) in enumerate(polygons):
        # ignore the room ceiling
        if plane_type == 'ceiling' and semantic_type not in ['door', 'window']:
            continue

        plane_vis = open3d.geometry.TriangleMesh()

        plane_vis.vertices = open3d.geometry.Vector3dVector(vertices)
        plane_vis.triangles = open3d.geometry.Vector3iVector(faces)

        if args.color == 'normal':
            if np.dot(normal, [1, 0, 0]) > eps:
                plane_vis.paint_uniform_color(colormap[0])
            elif np.dot(normal, [-1, 0, 0]) > eps:
                plane_vis.paint_uniform_color(colormap[1])
            elif np.dot(normal, [0, 1, 0]) > eps:
                plane_vis.paint_uniform_color(colormap[2])
            elif np.dot(normal, [0, -1, 0]) > eps:
                plane_vis.paint_uniform_color(colormap[3])
            elif np.dot(normal, [0, 0, 1]) > eps:
                plane_vis.paint_uniform_color(colormap[4])
            elif np.dot(normal, [0, 0, -1]) > eps:
                plane_vis.paint_uniform_color(colormap[5])
            else:
                plane_vis.paint_uniform_color(colormap[6])
        elif args.color == 'manhattan':
            # paint each plane with manhattan world
            if planeID not in manhattan.keys():
                plane_vis.paint_uniform_color(colormap[6])
            else:
                plane_vis.paint_uniform_color(colormap[manhattan[planeID]])

        plane_set.append(plane_vis)

    draw_geometries_with_back_face(plane_set)


def plot_floorplan(annos, polygons):
    """plot floorplan
    """
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    junctions = np.array([junc['coordinate'][:2] for junc in annos['junctions']])
    for (polygon, poly_type) in polygons:
        polygon = Polygon(junctions[np.array(polygon)])
        plot_coords(ax, polygon.exterior, alpha=0.5)
        if poly_type == 'outwall':
            patch = PolygonPatch(polygon, facecolor=semantics_cmap[poly_type], alpha=0)
        else:
            patch = PolygonPatch(polygon, facecolor=semantics_cmap[poly_type], alpha=0.5)
        ax.add_patch(patch)

    plt.axis('equal')
    plt.axis('off')
    plt.savefig('floorplan.png')
    plt.show()


def visualize_floorplan(annos):
    """visualize floorplan
    """
    # extract the floor in each semantic for floorplan visualization
    planes = []
    for semantic in annos['semantics']:
        for planeID in semantic['planeID']:
            if annos['planes'][planeID]['type'] == 'floor':
                planes.append({'planeID': planeID, 'type': semantic['type']})

        if semantic['type'] == 'outwall':
            outerwall_planes = semantic['planeID']

    # extract hole vertices
    lines_holes = []
    for semantic in annos['semantics']:
        if semantic['type'] in ['window', 'door']:
            for planeID in semantic['planeID']:
                lines_holes.extend(np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist())
    lines_holes = np.unique(lines_holes)

    # junctions on the floor
    junctions = np.array([junc['coordinate'] for junc in annos['junctions']])
    junction_floor = np.where(np.isclose(junctions[:, -1], 0))[0]

    # construct each polygon
    polygons = []
    for plane in planes:
        lineIDs = np.where(np.array(annos['planeLineMatrix'][plane['planeID']]))[0].tolist()
        junction_pairs = [np.where(np.array(annos['lineJunctionMatrix'][lineID]))[0].tolist() for lineID in lineIDs]
        polygon = convert_lines_to_vertices(junction_pairs)
        polygons.append([polygon[0], plane['type']])

    outerwall_floor = []
    for planeID in outerwall_planes:
        lineIDs = np.where(np.array(annos['planeLineMatrix'][planeID]))[0].tolist()
        lineIDs = np.setdiff1d(lineIDs, lines_holes)
        junction_pairs = [np.where(np.array(annos['lineJunctionMatrix'][lineID]))[0].tolist() for lineID in lineIDs]
        for start, end in junction_pairs:
            if start in junction_floor and end in junction_floor:
                outerwall_floor.append([start, end])

    outerwall_polygon = convert_lines_to_vertices(outerwall_floor)
    polygons.append([outerwall_polygon[0], 'outwall'])

    plot_floorplan(annos, polygons)


def parse_args():
    parser = argparse.ArgumentParser(description="Structured3D 3D Visualization")
    parser.add_argument("--path", required=True,
                        help="dataset path", metavar="DIR")
    parser.add_argument("--scene", required=True,
                        help="scene id", type=int)
    parser.add_argument("--type", choices=("floorplan", "wireframe", "plane"),
                        default="plane", type=str)
    parser.add_argument("--color", choices=["normal", "manhattan"],
                        default="normal", type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    # load annotations from json
    with open(os.path.join(args.path, "scene_%05d" % (args.scene, ), 'annotation_3d.json')) as file:
        annos = json.load(file)

    if args.type == "wireframe":
        visualize_wireframe(annos)
    elif args.type == "plane":
        visualize_plane(annos, args)
    elif args.type == "floorplan":
        visualize_floorplan(annos)


if __name__ == "__main__":
    main()
