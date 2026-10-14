import json
import os

import torch
import torchvision.io
import torchvision.transforms.v2
import torchvision.tv_tensors

s_name = "2026-08-09@036"
a_image = torchvision.io.read_image(f"runtime/raw/{s_name}.png")
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
a_boxes = torchvision.tv_tensors.BoundingBoxes(l_bboxes, format="XYXY", canvas_size=a_image.shape[-2:])
a_indexes = torch.arange(len(l_labels))

o_transform = torchvision.transforms.v2.Compose([
    torchvision.transforms.v2.RandomHorizontalFlip(p=0.5),
    torchvision.transforms.v2.RandomRotation(degrees=15),
    torchvision.transforms.v2.ColorJitter(brightness=0.2, contrast=0.2),
    torchvision.transforms.v2.GaussianBlur(kernel_size=5),
    torchvision.transforms.v2.SanitizeBoundingBoxes(),
])

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(5):
    a_output, d_target = o_transform(a_image, {"boxes": a_boxes, "labels": a_indexes})
    torchvision.io.write_png(a_output, f"runtime/output/{i_index}.png")

    l_shapes = []
    for l_bbox, i_label in zip(d_target["boxes"].tolist(), d_target["labels"].tolist()):
        f_x1, f_y1, f_x2, f_y2 = l_bbox
        l_points = [[f_x1, f_y1], [f_x2, f_y2]]
        l_shapes.append({"label": l_labels[i_label], "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
