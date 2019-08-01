## Data Organization

There is a separate subdirectory for every scene, which is named by a unique ID. Within each scene directory, there are separate directories for different types of data as follows:

```shell
<sceneID>
|-- 2D_rendering
    |-- <roomID>
        |-- panorama
            |-- <empty/simple/full>
                different furniture configurations
                |-- rgb_<cold/raw/warm>light.png
                    photo-realistic rendered rgb images under different lighting conditions
                |-- semantic.png
                    semantic segmentation
                |-- albedo.png
                    albedo
                |-- depth.png
                    depth
                |-- normal.png
                    surface normal
            |-- layout.txt
                room layout annotation
            |-- camera_xyz.txt
                camera global location
|-- annotation_3d.json
    primitive and relationship based structure annotations
```

### Annotation Format

For each scene, the annotation contains the following information:

**Structure annotation (`annotation_3d.json`)**: primitive and relationship based representation. See all the room types [here](assets/room_types.txt).

```shell
{
  // PRIMITVIES
  "junctions":[
    {
      "coordinate": [0.0, 0.0, 0.0]
    }
  ],
  "lines": [
    {
      "point": [0.0, 0.0, 0.0], 
      "direction": [0.0, 1.0, 0.0]
    }
  ],
  "planes": [
    {
      "normal": [1.0, 0.0, 0.0], // the normal points to the empty space
      "offset": 0.0,
      "type": "..." // ceiling, floor, wall
    }
  ],
  // RELATIONSHIPS
  "semantics": [
    {
      "planeID": [indices of the planes],
      "type": "..." // room type, door, window
    }
  ],
  // matrix W_1 where the ij-th entry is 1 iff l_i is on p_j
  "planeLineMatrix": [
    ...
  ],
  // matrix W_2 here the mn-th entry is 1 iff x_m is on l_nj
  "lineJunctionMatrix": [
    ...
  ],
  // OTHERS
  "cuboids": [
    [indices of the planes],
    ...
  ],
  "manhattan": [
    [indices of the planes],
    ...
  ]
}
```

**Semantic annotation (`semantic.png`)**: unsigned 8-bit integers within a PNG. We use [NYUv2](https://cs.nyu.edu/~silberman/datasets/nyu_depth_v2) 40-label set, see all the label ids [here](assets/labelids.txt).

**Albedo data (`albedo.png`)**: unsigned 8-bit integers within a PNG.

**Depth data (`depth.png`)**: unsigned 16-bit integers within a PNG. The units are millimeters, a value of 1000 is a meter. A zero value denotes 'no reading'.

**Normal data (`normal.png`)**: unsigned 8-bit integers within a PNG (x, y, z), where the integer values in the file are 128 \* (1 + n), where n is a normal coordinate in range [-1, 1].

**Layout annotation (`layout.txt`)**: a list of 2D positions of the corner (from top to bottom, from left to right) in the image space

```shell
x_0 y_ceiling_0
x_0 y_floor_0
x_1 y_ceiling_1
x_1 y_floor_1
...
```
which follows the order of layout.

**Camera location (`camera_xyz.txt`)**: For each panoramic image, we only store the camera location in global coordinates. The direction of the camera is always along the negative y-axis. Global coordinate system is arbitrary, but the z-axis generally points upward.
