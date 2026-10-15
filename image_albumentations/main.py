import json
import os
import shutil

import albumentations
import albumentations.augmentations.geometric.functional
import albumentations.augmentations.pixel.functional
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


def apply_plasma_brightness_contrast(img, brightness_factor, contrast_factor, plasma_pattern):  # 官方的 multiply 會把負數結果夾成 0，亮度、對比設成負值（變暗、降對比）完全沒效果，這裡改用一般的數學運算
    a_float = img.astype(numpy.float32)
    f_max = 255.0 if img.dtype == numpy.uint8 else 1.0
    a_float = a_float / f_max
    a_pattern = plasma_pattern[..., numpy.newaxis] if img.ndim == 3 else plasma_pattern
    a_float = a_float + a_pattern * brightness_factor
    f_mean = a_float.mean()
    a_weights = a_pattern * contrast_factor + 1
    a_float = a_float * a_weights + f_mean * (1 - a_weights)
    a_float = numpy.clip(a_float, 0, 1) * f_max
    return a_float.astype(img.dtype) if img.dtype != numpy.uint8 else numpy.round(a_float).astype(numpy.uint8)


albumentations.augmentations.pixel.functional.apply_plasma_brightness_contrast = apply_plasma_brightness_contrast


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


def to_json_value(o_value):  # 把這次轉換抽到的參數轉成能寫進 json 的值：numpy 純量轉成 python 數字，小的陣列（例如 3x3 的矩陣）轉成清單，大的陣列（雜訊圖、位移表）只留形狀和範圍
    if isinstance(o_value, dict):
        d_result = {}
        for s_key, o_item in o_value.items():
            d_result[s_key] = to_json_value(o_item)
        return d_result
    if isinstance(o_value, (list, tuple)):
        l_result = []
        for o_item in o_value:
            l_result.append(to_json_value(o_item))
        return l_result
    if isinstance(o_value, numpy.ndarray):
        if o_value.size <= 20:
            return o_value.tolist()
        return {"shape": list(o_value.shape), "min": float(o_value.min()), "max": float(o_value.max())}
    if isinstance(o_value, numpy.generic):
        return o_value.item()
    if isinstance(o_value, (int, float, str, bool)) or o_value is None:
        return o_value
    return str(o_value)


with open("config.yaml", encoding="utf-8") as o_file:
    d_config = yaml.safe_load(o_file)
s_name = d_config["name"]
i_count = d_config["count"]
d_bbox = d_config["bbox"]
d_transforms = d_config["transforms"]

a_bgr_image = cv2.imread(f"runtime/raw/{s_name}.png")
a_image = cv2.cvtColor(a_bgr_image, cv2.COLOR_BGR2RGB)  # cv2 讀進來是 BGR，Albumentations 的色彩轉換（RGBShift、ChannelDropout、色溫等）假設是 RGB，先轉成 RGB
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
o_transform = albumentations.Compose(l_transforms, bbox_params=o_bbox_params, save_applied_params=True)  # save_applied_params 讓結果帶回這張實際用了哪些轉換、抽到什麼參數

shutil.rmtree("runtime/output", ignore_errors=True)  # 先清掉舊的輸出，避免殘留上次多出來的檔案
os.makedirs("runtime/output")
for i_index in range(i_count):
    d_result = o_transform(image=a_image, bboxes=l_bboxes, l_labels=l_labels)
    a_output = d_result["image"]
    a_bgr_output = cv2.cvtColor(a_output, cv2.COLOR_RGB2BGR)  # 存檔前轉回 BGR，cv2.imwrite 才會存對顏色
    cv2.imwrite(f"runtime/output/{i_index}.png", a_bgr_output)

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
    l_applied = []
    for s_applied_name, d_applied_params in d_result["applied_transforms"]:
        l_applied.append({"name": s_applied_name, "params": to_json_value(d_applied_params)})
    with open(f"runtime/output/{i_index}.transforms.json", "w") as o_file:
        json.dump(l_applied, o_file, ensure_ascii=False, indent=2)  # 這張圖實際用了哪些轉換、抽到的參數，之後可以回頭查
    l_applied_names = [d_applied["name"] for d_applied in l_applied]
    print(f"轉換完成 {i_index + 1}/{i_count}: runtime/output/{i_index}.png  用了: {', '.join(l_applied_names)}")
