import json
import os
import shutil

import albumentations
import albumentations.augmentations.geometric.functional
import albumentations.core.bbox_utils
import cv2
import numpy
import yaml


class MorphologicalPerBox(albumentations.Morphological):  # 官方的 Morphological 把所有框的 mask 疊成 3 維丟給 cv2，框一多就報 dims <= 2，這裡改成一個框一個框做

    def apply_to_bboxes(self, bboxes, kernel, **params):
        l_shape = params["shape"][:2]
        a_boxes = albumentations.core.bbox_utils.denormalize_bboxes(bboxes, l_shape)
        a_masks = albumentations.augmentations.geometric.functional.masks_from_bboxes(a_boxes, l_shape)
        l_masks = []
        for a_mask in a_masks:
            a_result = albumentations.augmentations.geometric.functional.morphology(a_mask, kernel, self.operation)
            l_masks.append(a_result)
        a_boxes[:, :4] = albumentations.augmentations.geometric.functional.bboxes_from_masks(numpy.stack(l_masks))
        return albumentations.core.bbox_utils.normalize_bboxes(a_boxes, l_shape)


def create_piecewise_affine_maps(image_shape, grid, scale, absolute_scale, random_generator):  # 官方 2.0.8 的 PiecewiseAffine 把「控制點的目標座標」直接加權平均成整張 map，不管 scale 多小都會嚴重變形，這裡改成「原座標 + 平滑的位移」，scale 才有作用
    i_height, i_width = image_shape[:2]
    i_rows, i_cols = grid
    if scale <= 0:
        return None, None
    f_jitter_scale = scale / 3 if absolute_scale else scale * min(i_width, i_height) / 3
    a_jitter = random_generator.normal(0, f_jitter_scale, (i_rows, i_cols, 2)).astype(numpy.float32)
    a_dy = cv2.resize(a_jitter[:, :, 0], (i_width, i_height), interpolation=cv2.INTER_CUBIC)  # 控制點的位移放大成整張圖的平滑位移
    a_dx = cv2.resize(a_jitter[:, :, 1], (i_width, i_height), interpolation=cv2.INTER_CUBIC)
    a_xx, a_yy = numpy.meshgrid(numpy.arange(i_width, dtype=numpy.float32), numpy.arange(i_height, dtype=numpy.float32))
    a_map_x = numpy.clip(a_xx + a_dx, 0, i_width - 1)
    a_map_y = numpy.clip(a_yy + a_dy, 0, i_height - 1)
    return a_map_x, a_map_y


albumentations.augmentations.geometric.functional.create_piecewise_affine_maps = create_piecewise_affine_maps


def to_tuple(o_value):  # yaml 的 [a, b] 讀進來是 list，Albumentations 的範圍和尺寸參數要 tuple，遞迴轉過去
    if isinstance(o_value, dict):
        d_result = {}
        for s_key, o_item in o_value.items():
            d_result[s_key] = to_tuple(o_item)
        return d_result
    if isinstance(o_value, list):
        l_result = []
        for o_item in o_value:
            l_result.append(to_tuple(o_item))
        return tuple(l_result)
    return o_value


with open("config.yaml", encoding="utf-8") as o_file:
    d_config = yaml.safe_load(o_file)
s_name = d_config["name"]
i_count = d_config["count"]
d_bbox = d_config["bbox"]
d_transforms = d_config["transforms"]

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

# config.yaml 的 transforms 每一項是 Albumentations 的類別名稱加參數，依序建立；p 是 0 的就不放進去
l_transforms = []
for s_transform_name, d_params in d_transforms.items():
    if d_params.get("p", 0.5) == 0:
        continue
    o_class = getattr(albumentations, s_transform_name)
    if s_transform_name == "Morphological":
        o_class = MorphologicalPerBox
    l_transforms.append(o_class(**to_tuple(d_params)))
print(f"啟用的轉換: {len(l_transforms)} 個")

o_bbox_params = albumentations.BboxParams(format="pascal_voc", label_fields=["l_labels"], min_area=d_bbox["min_area"], min_visibility=d_bbox["min_visibility"])
o_transform = albumentations.Compose(l_transforms, bbox_params=o_bbox_params)

shutil.rmtree("runtime/output", ignore_errors=True)  # 先清掉舊的輸出，避免殘留上次多出來的檔案
os.makedirs("runtime/output")
for i_index in range(i_count):
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
    print(f"轉換完成 {i_index + 1}/{i_count}: runtime/output/{i_index}.png")
