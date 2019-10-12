import os
import json
import argparse

import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from descartes.patch import PolygonPatch

from misc.panorama import draw_boundary_from_cor_id
from misc.colors import colormap_255


def visualize_panorama(args):
    """visualize panorama layout
    """
    scene_path = os.path.join(args.path, "scene_%05d" % (args.scene, ), "2D_rendering")

    for room_id in np.sort(os.listdir(scene_path)):
        room_path = os.path.join(scene_path, room_id, "panorama")

        cor_id = np.loadtxt(os.path.join(room_path, "layout.txt"))
        img_src = io.imread(os.path.join(room_path, "full", "rgb_rawlight.png"))
        img_viz = draw_boundary_from_cor_id(cor_id, img_src)

        plt.axis('off')
        plt.imshow(img_viz)
        plt.show()


def visualize_perspective(args):
    """visualize perspective layout
    """
    colors = np.array(colormap_255) / 255

    scene_path = os.path.join(args.path, "scene_%05d" % (args.scene, ), "2D_rendering")

    for room_id in np.sort(os.listdir(scene_path)):
        room_path = os.path.join(scene_path, room_id, "perspective", "full")

        for position_id in np.sort(os.listdir(room_path)):
            position_path = os.path.join(room_path, position_id)

            image = io.imread(os.path.join(position_path, "rgb_rawlight.png"))
            with open(os.path.join(position_path, "layout.json")) as f:
                annos = json.load(f)

            fig = plt.figure()
            for i, key in enumerate(['amodal_mask', 'visible_mask']):
                ax = fig.add_subplot(2, 1, i + 1)
                plt.axis('off')
                plt.imshow(image)

                for i, planes in enumerate(annos['planes']):
                    if len(planes[key]):
                        for plane in planes[key]:
                            polygon = Polygon([annos['junctions'][id]['coordinate'] for id in plane])
                            patch = PolygonPatch(polygon, facecolor=colors[i], alpha=0.5)
                            ax.add_patch(patch)

                plt.title(key)
            plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Structured3D 2D Layout Visualization")
    parser.add_argument("--path", required=True,
                        help="dataset path", metavar="DIR")
    parser.add_argument("--scene", required=True,
                        help="scene id", type=int)
    parser.add_argument("--type", choices=["perspective", "panorama"], required=True,
                        help="type of camera", type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    if args.type == 'panorama':
        visualize_panorama(args)
    elif args.type == 'perspective':
        visualize_perspective(args)


if __name__ == "__main__":
    main()
