import os
import argparse

import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
from misc.panorama import draw_boundary_from_cor_id


def parse_args():
    parser = argparse.ArgumentParser(description="Structured3D 2D Layout Visualization")
    parser.add_argument("--path", required=True,
                        help="dataset path", metavar="DIR")
    parser.add_argument("--name", required=True,
                        help="scene name", type=str)
    parser.add_argument("--type", choices=["empty", "simple", "full"],
                        help="type of furniture configurations",
                        default="full", type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    
    for room in np.sort(os.listdir(os.path.join(args.path, args.name, "2D_rendering"))):
        print(f"scene: {args.name:}, room: {room:}")
        room_path = os.path.join(args.path, args.name, "2D_rendering", room, "panorama")

        cor_id = np.loadtxt(os.path.join(room_path, "layout.txt"))
        img_src = io.imread(os.path.join(room_path, args.type, "rgb_rawlight.png"))
        img_viz = draw_boundary_from_cor_id(cor_id, img_src)

        plt.axis('off')
        plt.imshow(img_viz)
        plt.show()


if __name__ == "__main__":
    main()
