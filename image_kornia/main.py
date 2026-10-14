import json
import os

import kornia.augmentation
import torch
import torchvision.io
import torchvision.utils

s_name = "2026-08-09@036"
a_uint8 = torchvision.io.read_image(f"runtime/raw/{s_name}.png")
a_image = a_uint8.float().unsqueeze(0) / 255
i_height, i_width = a_image.shape[-2:]
with open(f"runtime/raw/{s_name}.json") as o_file:
    d_label = json.load(o_file)

l_bboxes = []
l_labels = []
for d_shape in d_label["shapes"]:
    l_xs = [l_point[0] for l_point in d_shape["points"]]
    l_ys = [l_point[1] for l_point in d_shape["points"]]
    f_x1 = min(l_xs)
    f_y1 = min(l_ys)
    f_x2 = max(l_xs)
    f_y2 = max(l_ys)
    l_bboxes.append([f_x1, f_y1, f_x2, f_y2])
    l_labels.append(d_shape["label"])
a_boxes = torch.tensor([l_bboxes])

o_transform = kornia.augmentation.AugmentationSequential(
    kornia.augmentation.RandomHorizontalFlip(p=0.5),
    kornia.augmentation.RandomRotation(degrees=15, p=0.5),
    kornia.augmentation.ColorJitter(brightness=0.2, contrast=0.2, p=0.5),
    kornia.augmentation.RandomGaussianNoise(std=0.05, p=0.5),
    data_keys=["input", "bbox_xyxy"],
)

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(5):
    a_output, a_out_boxes = o_transform(a_image, a_boxes)
    torchvision.utils.save_image(a_output, f"runtime/output/{i_index}.png")

    l_shapes = []
    for l_bbox, s_label in zip(a_out_boxes[0].tolist(), l_labels):
        f_x1 = max(l_bbox[0], 0)
        f_y1 = max(l_bbox[1], 0)
        f_x2 = min(l_bbox[2], i_width)
        f_y2 = min(l_bbox[3], i_height)
        if f_x2 - f_x1 < 1 or f_y2 - f_y1 < 1:
            continue
        l_points = [[f_x1, f_y1], [f_x2, f_y2]]
        l_shapes.append({"label": s_label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
