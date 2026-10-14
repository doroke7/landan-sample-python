import json
import os

import albumentations
import cv2

s_name = "2026-08-09@036"
a_image = cv2.imread(f"runtime/raw/{s_name}.png")
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

o_transform = albumentations.Compose(
    [
        albumentations.HorizontalFlip(p=0.5),
        albumentations.Rotate(limit=15, p=0.5),
        albumentations.RandomBrightnessContrast(p=0.5),
        albumentations.GaussNoise(p=0.5),
    ],
    bbox_params=albumentations.BboxParams(format="pascal_voc", label_fields=["l_labels"]),
)

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(5):
    d_result = o_transform(image=a_image, bboxes=l_bboxes, l_labels=l_labels)
    a_output = d_result["image"]
    cv2.imwrite(f"runtime/output/{i_index}.png", a_output)

    l_shapes = []
    for l_bbox, s_label in zip(d_result["bboxes"], d_result["l_labels"]):
        f_x1, f_y1, f_x2, f_y2 = l_bbox[:4]
        l_points = [[float(f_x1), float(f_y1)], [float(f_x2), float(f_y2)]]
        l_shapes.append({"label": s_label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
