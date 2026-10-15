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

o_random_iou_crop = torchvision.transforms.v2.RandomIoUCrop()                                                           # 隨機裁切，裁出來的區域和框的 IoU 要夠大，輸出尺寸會變
o_random_resized_crop = torchvision.transforms.v2.RandomResizedCrop(size=(720, 1280), scale=(0.5, 1.0), antialias=True)  # 隨機裁切一塊（面積 50% 到 100%）再縮回 720x1280
o_random_crop = torchvision.transforms.v2.RandomCrop(size=(576, 1024), pad_if_needed=True)                               # 隨機位置裁成 576x1024，畫面比較小就先補邊
o_center_crop = torchvision.transforms.v2.CenterCrop(size=(576, 1024))                                                   # 中心裁成 576x1024
o_random_horizontal_flip = torchvision.transforms.v2.RandomHorizontalFlip(p=1.0)                                         # 左右翻轉
o_random_vertical_flip = torchvision.transforms.v2.RandomVerticalFlip(p=1.0)                                             # 上下翻轉
o_random_rotation = torchvision.transforms.v2.RandomRotation(degrees=15)                                                 # 旋轉，角度範圍 -15 到 15 度，框變成旋轉後的外接矩形
o_random_affine = torchvision.transforms.v2.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1), shear=10)   # 旋轉、平移 ±10%、縮放 0.9 到 1.1 倍、傾斜 ±10 度一起做
o_random_perspective = torchvision.transforms.v2.RandomPerspective(distortion_scale=0.3, p=1.0)                          # 透視變形，distortion_scale 範圍 0 到 1
o_elastic_transform = torchvision.transforms.v2.ElasticTransform(alpha=50.0, sigma=5.0)                                  # 彈性扭曲，框可能不準
o_random_zoom_out = torchvision.transforms.v2.RandomZoomOut(side_range=(1.0, 1.5), p=1.0)                                # 畫面縮小放到更大的黑色畫布上，輸出尺寸會變大
o_scale_jitter = torchvision.transforms.v2.ScaleJitter(target_size=(720, 1280), scale_range=(0.5, 1.5))                  # 隨機縮放 0.5 到 1.5 倍，輸出尺寸會變
o_random_shortest_size = torchvision.transforms.v2.RandomShortestSize(min_size=[400, 500, 600], max_size=1400)           # 最短邊隨機縮到 400、500、600 其中一個，等比
o_random_resize = torchvision.transforms.v2.RandomResize(min_size=400, max_size=700)                                     # 最短邊隨機縮到 400 到 700，等比
o_resize = torchvision.transforms.v2.Resize(size=(360, 640), antialias=True)                                             # 縮成 360x640
o_pad = torchvision.transforms.v2.Pad(padding=20)                                                                        # 四邊補 20 像素黑邊
o_color_jitter = torchvision.transforms.v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.02)           # 亮度、對比、飽和度、色相抖動，hue 範圍 0 到 0.5
o_random_photometric_distort = torchvision.transforms.v2.RandomPhotometricDistort(p=1.0)                                 # SSD 的色彩扭曲：亮度、對比、色相、飽和度、通道順序隨機
o_random_channel_permutation = torchvision.transforms.v2.RandomChannelPermutation()                                      # R、G、B 通道隨機換位
o_random_grayscale = torchvision.transforms.v2.RandomGrayscale(p=1.0)                                                    # 轉灰階（還是 3 個通道）
o_random_invert = torchvision.transforms.v2.RandomInvert(p=1.0)                                                          # 顏色反相
o_random_posterize = torchvision.transforms.v2.RandomPosterize(bits=4, p=1.0)                                            # 減少色階，bits 範圍 1 到 8
o_random_solarize = torchvision.transforms.v2.RandomSolarize(threshold=128.0, p=1.0)                                     # 曝光過度，高於 threshold 的像素反相，範圍 0 到 255
o_random_autocontrast = torchvision.transforms.v2.RandomAutocontrast(p=1.0)                                              # 自動對比
o_random_equalize = torchvision.transforms.v2.RandomEqualize(p=1.0)                                                      # 直方圖均衡化
o_random_adjust_sharpness = torchvision.transforms.v2.RandomAdjustSharpness(sharpness_factor=2.0, p=1.0)                 # 調整銳利度，0 是模糊、1 是不變、2 是銳化
o_gaussian_blur = torchvision.transforms.v2.GaussianBlur(kernel_size=5)                                                  # 高斯模糊，kernel_size 要是奇數
o_jpeg = torchvision.transforms.v2.JPEG(quality=(50, 95))                                                                # JPEG 壓縮失真，quality 範圍 1 到 100
o_random_erasing = torchvision.transforms.v2.RandomErasing(p=1.0, scale=(0.02, 0.1))                                     # 隨機擦掉一塊，scale 是面積比例
o_to_float = torchvision.transforms.v2.ToDtype(torch.float32, scale=True)                                                # GaussianNoise 只吃浮點數，先轉成 float32（0 到 1）
o_gaussian_noise_core = torchvision.transforms.v2.GaussianNoise(mean=0.0, sigma=0.05)                                    # 高斯雜訊，sigma 是標準差，以 0 到 1 的像素值為基準
o_to_uint8 = torchvision.transforms.v2.ToDtype(torch.uint8, scale=True)                                                  # 轉回 uint8，才能存 png
o_gaussian_noise = torchvision.transforms.v2.Compose([o_to_float, o_gaussian_noise_core, o_to_uint8])                    # 高斯雜訊（轉 float、加雜訊、轉回 uint8 三步合成一個）

# RandomApply 的 p 是觸發機率，0 是不用，1 是每張都做；固定尺寸的裁切放最前面、最後一定要 SanitizeBoundingBoxes 移除被轉到畫面外或太小的框
o_sanitize = torchvision.transforms.v2.SanitizeBoundingBoxes()  # 移除被轉到畫面外或太小的框
o_transform = torchvision.transforms.v2.Compose([
    torchvision.transforms.v2.RandomApply([o_random_iou_crop], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_resized_crop], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_crop], p=0.3),
    torchvision.transforms.v2.RandomApply([o_center_crop], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_horizontal_flip], p=0.5),
    torchvision.transforms.v2.RandomApply([o_random_vertical_flip], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_rotation], p=0.5),
    torchvision.transforms.v2.RandomApply([o_random_affine], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_perspective], p=0.3),
    torchvision.transforms.v2.RandomApply([o_elastic_transform], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_zoom_out], p=0.3),
    torchvision.transforms.v2.RandomApply([o_scale_jitter], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_shortest_size], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_resize], p=0.3),
    torchvision.transforms.v2.RandomApply([o_resize], p=0.3),
    torchvision.transforms.v2.RandomApply([o_pad], p=0.3),
    torchvision.transforms.v2.RandomApply([o_color_jitter], p=0.5),
    torchvision.transforms.v2.RandomApply([o_random_photometric_distort], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_channel_permutation], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_grayscale], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_invert], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_posterize], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_solarize], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_autocontrast], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_equalize], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_adjust_sharpness], p=0.3),
    torchvision.transforms.v2.RandomApply([o_gaussian_blur], p=0.5),
    torchvision.transforms.v2.RandomApply([o_jpeg], p=0.3),
    torchvision.transforms.v2.RandomApply([o_random_erasing], p=0.3),
    torchvision.transforms.v2.RandomApply([o_gaussian_noise], p=0.3),
    o_sanitize,
])

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(50):
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
