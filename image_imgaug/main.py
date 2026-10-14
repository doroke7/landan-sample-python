import json
import os

import cv2
import imgaug.augmentables.bbs
import imgaug.augmenters

s_name = "2026-08-09@036"
a_image = cv2.imread(f"runtime/raw/{s_name}.png")
with open(f"runtime/raw/{s_name}.json") as o_file:
    d_label = json.load(o_file)

l_boxes = []
for d_shape in d_label["shapes"]:
    l_xs = [l_point[0] for l_point in d_shape["points"]]
    l_ys = [l_point[1] for l_point in d_shape["points"]]
    f_x1 = min(l_xs)
    f_y1 = min(l_ys)
    f_x2 = max(l_xs)
    f_y2 = max(l_ys)
    l_boxes.append(imgaug.augmentables.bbs.BoundingBox(x1=f_x1, y1=f_y1, x2=f_x2, y2=f_y2, label=d_shape["label"]))
o_boxes = imgaug.augmentables.bbs.BoundingBoxesOnImage(l_boxes, shape=a_image.shape)

o_transform = imgaug.augmenters.Sequential([
    imgaug.augmenters.Fliplr(0.5),
    imgaug.augmenters.Affine(rotate=(-15, 15)),
    imgaug.augmenters.Multiply((0.8, 1.2)),
    imgaug.augmenters.AdditiveGaussianNoise(scale=(0, 10)),
])

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(5):
    a_output, o_out_boxes = o_transform(image=a_image, bounding_boxes=o_boxes)
    o_out_boxes = o_out_boxes.clip_out_of_image()
    cv2.imwrite(f"runtime/output/{i_index}.png", a_output)

    l_shapes = []
    for o_box in o_out_boxes.bounding_boxes:
        l_points = [[float(o_box.x1), float(o_box.y1)], [float(o_box.x2), float(o_box.y2)]]
        l_shapes.append({"label": o_box.label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
