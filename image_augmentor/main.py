import json
import os
import random

import Augmentor.Operations
import numpy
import PIL.Image
import PIL.ImageDraw

s_name = "2026-08-09@036"
o_image = PIL.Image.open(f"runtime/raw/{s_name}.png").convert("RGB")
with open(f"runtime/raw/{s_name}.json") as o_file:
    d_label = json.load(o_file)

# Augmentor 沒有 bbox，每個框畫成一張 mask，跟圖一起轉，再從 mask 還原框
l_masks = []
l_labels = []
for d_shape in d_label["shapes"]:
    l_xs = [l_point[0] for l_point in d_shape["points"]]
    l_ys = [l_point[1] for l_point in d_shape["points"]]
    f_x1 = min(l_xs)
    f_y1 = min(l_ys)
    f_x2 = max(l_xs)
    f_y2 = max(l_ys)
    o_mask = PIL.Image.new("L", o_image.size, 0)
    o_draw = PIL.ImageDraw.Draw(o_mask)
    o_draw.rectangle([f_x1, f_y1, f_x2, f_y2], fill=255)
    l_masks.append(o_mask)
    l_labels.append(d_shape["label"])

o_flip = Augmentor.Operations.Flip(probability=0.5, top_bottom_left_right="LEFT_RIGHT")
o_rotate = Augmentor.Operations.RotateRange(probability=0.5, max_left_rotation=15, max_right_rotation=15)
o_brightness = Augmentor.Operations.RandomBrightness(probability=0.5, min_factor=0.8, max_factor=1.2)

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(5):
    l_images = [o_image] + l_masks
    if random.random() < 0.5:
        l_images = o_flip.perform_operation(l_images)
    if random.random() < 0.5:
        l_images = o_rotate.perform_operation(l_images)
    l_image = [l_images[0]]
    if random.random() < 0.5:
        l_image = o_brightness.perform_operation(l_image)
    l_image[0].save(f"runtime/output/{i_index}.png")

    l_shapes = []
    for o_mask, s_label in zip(l_images[1:], l_labels):
        a_mask = numpy.array(o_mask)
        a_ys, a_xs = numpy.nonzero(a_mask > 127)
        if len(a_xs) == 0:
            continue
        f_x1 = float(a_xs.min())
        f_y1 = float(a_ys.min())
        f_x2 = float(a_xs.max() + 1)
        f_y2 = float(a_ys.max() + 1)
        l_points = [[f_x1, f_y1], [f_x2, f_y2]]
        l_shapes.append({"label": s_label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
