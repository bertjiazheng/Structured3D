import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon

from misc.colors import semantics_cmap
from misc.utils import get_corners_of_bb3d_no_index


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


def visualize_floorplan(args):
    """visualize floorplan
    """
    with open(os.path.join(args.path, f"scene_{args.scene:05d}", "annotation_3d.json")) as file:
        annos = json.load(file)

    with open(os.path.join(args.path, f"scene_{args.scene:05d}", "bbox_3d.json")) as file:
        boxes = json.load(file)

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

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    junctions = np.array([junc['coordinate'][:2] for junc in annos['junctions']])
    for (polygon, poly_type) in polygons:
        polygon = np.array(polygon + [polygon[0], ])
        polygon = Polygon(junctions[polygon])
        if poly_type == 'outwall':
            plot_polygon(polygon, ax=ax, add_points=False, facecolor=semantics_cmap[poly_type], alpha=0)
        else:
            plot_polygon(polygon, ax=ax, add_points=False, facecolor=semantics_cmap[poly_type], alpha=0.5)

    for bbox in boxes:
        basis = np.array(bbox['basis'])
        coeffs = np.array(bbox['coeffs'])
        centroid = np.array(bbox['centroid'])

        corners = get_corners_of_bb3d_no_index(basis, coeffs, centroid)
        corners = corners[[0, 1, 2, 3, 0], :2]

        polygon = Polygon(corners)
        plot_polygon(polygon, ax=ax, add_points=False, facecolor=colors.rgb2hex(np.random.rand(3)), alpha=0.5)

    plt.axis('equal')
    plt.axis('off')
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Structured3D Floorplan Visualization")
    parser.add_argument("--path", required=True,
                        help="dataset path", metavar="DIR")
    parser.add_argument("--scene", required=True,
                        help="scene id", type=int)
    return parser.parse_args()


def main():
    args = parse_args()

    visualize_floorplan(args)


if __name__ == "__main__":
    main()
