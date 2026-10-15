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

o_transform = kornia.augmentation.AugmentationSequential(                                                                          # bbox_xyxy 讓框跟圖一起轉
    kornia.augmentation.RandomHorizontalFlip(p=1.0),                                                                               # 左右翻轉，p=1.0 因為 random_apply 已先挑過
    kornia.augmentation.RandomVerticalFlip(p=1.0),                                                                                 # 上下翻轉
    kornia.augmentation.RandomRotation(degrees=20, resample="BILINEAR", p=1.0),                                                    # 旋轉 -20 到 20 度，resample 是插值方式
    kornia.augmentation.RandomPerspective(distortion_scale=0.15, sampling_method="area_preserving", p=1.0),                        # 透視變形，area_preserving 黑邊較少
    kornia.augmentation.ColorJitter(brightness=(0.7, 1.3), contrast=(0.7, 1.3), saturation=(0.7, 1.3), hue=(-0.03, 0.03), p=1.0),  # 亮度、對比、飽和度 0.7 到 1.3 倍，色相 ±0.03
    kornia.augmentation.RandomGaussianBlur(kernel_size=(7, 7), sigma=(0.1, 1.5), border_type="reflect", p=1.0),                    # 高斯模糊，邊緣鏡射補齊
    kornia.augmentation.RandomGaussianNoise(mean=0.0, std=0.05, p=1.0),                                                            # 高斯雜訊，std 以 0 到 1 的像素值為基準
    random_apply=(3, 5),                                                                                                           # 每次從上面隨機挑 3 到 5 個轉換來做
    data_keys=["input", "bbox_xyxy"],                                                                                              # 同時轉圖和框
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
