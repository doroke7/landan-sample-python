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

o_flip_lr = Augmentor.Operations.Flip(probability=0.5, top_bottom_left_right="LEFT_RIGHT")                                                                                                    # 左右翻轉
o_flip_tb = Augmentor.Operations.Flip(probability=0.3, top_bottom_left_right="TOP_BOTTOM")                                                                                                    # 上下翻轉
o_flip_random = Augmentor.Operations.Flip(probability=0.3, top_bottom_left_right="RANDOM")                                                                                                    # 左右、上下、不翻 隨機選一個
o_rotate_90 = Augmentor.Operations.Rotate(probability=0.3, rotation=-1)                                                                                                                       # 隨機轉 90 / 180 / 270 度，-1 是隨機選，也可以固定寫 90、180、270
o_rotate_range = Augmentor.Operations.RotateRange(probability=0.5, max_left_rotation=15, max_right_rotation=15)                                                                               # 任意角度旋轉，左右各最多 15 度（範圍 0 到 25），會裁掉黑邊
o_rotate_standard = Augmentor.Operations.RotateStandard(probability=0.3, max_left_rotation=15, max_right_rotation=15, expand=False)                                                           # 任意角度旋轉，左右各最多 15 度（範圍 0 到 25），expand=False 不擴大畫布
o_skew_tilt = Augmentor.Operations.Skew(probability=0.3, skew_type="TILT", magnitude=0.3)                                                                                                     # 透視傾斜（上下左右選一邊），magnitude 範圍 0 到 1
o_skew_corner = Augmentor.Operations.Skew(probability=0.3, skew_type="CORNER", magnitude=0.3)                                                                                                 # 透視拉一個角，magnitude 範圍 0 到 1
o_shear = Augmentor.Operations.Shear(probability=0.3, max_shear_left=10, max_shear_right=10)                                                                                                  # 剪切，左右各最多 10 度（範圍 0 到 25）
o_scale = Augmentor.Operations.Scale(probability=0.3, scale_factor=1.2)                                                                                                                       # 等比放大 1.2 倍，範圍 1 以上，畫面會變大
o_zoom = Augmentor.Operations.Zoom(probability=0.3, min_factor=1.0, max_factor=1.3)                                                                                                           # 放大後裁回原尺寸，倍數 1.0 到 1.3
o_zoom_random = Augmentor.Operations.ZoomRandom(probability=0.3, percentage_area=0.8, randomise=True)                                                                                         # 隨機放大，保留 80% 面積，randomise 是面積也隨機
o_crop = Augmentor.Operations.Crop(probability=0.3, width=o_image.width * 4 // 5, height=o_image.height * 4 // 5, centre=False)                                                               # 裁固定尺寸（原圖 80%），centre=False 是隨機位置
o_crop_percentage = Augmentor.Operations.CropPercentage(probability=0.3, percentage_area=0.8, centre=False, randomise_percentage_area=True)                                                   # 依面積百分比裁切，80% 面積，位置和面積都隨機
o_crop_random = Augmentor.Operations.CropRandom(probability=0.3, percentage_area=0.8)                                                                                                         # 隨機位置裁切 80% 面積
o_resize = Augmentor.Operations.Resize(probability=0.3, width=o_image.width // 2, height=o_image.height // 2, resample_filter="BICUBIC")                                                      # 縮成固定尺寸（原圖一半），輸出尺寸會變
o_distort = Augmentor.Operations.Distort(probability=0.3, grid_width=4, grid_height=4, magnitude=8)                                                                                           # 格子扭曲，格數 4x4，magnitude 越大越歪
o_gaussian_distortion = Augmentor.Operations.GaussianDistortion(probability=0.3, grid_width=4, grid_height=4, magnitude=8, corner="bell", method="in", mex=0.5, mey=0.5, sdx=0.05, sdy=0.05)  # 高斯扭曲，corner=bell 是中心凸起，method=in 是往內

l_geometry = [
    o_crop,                 # 裁固定尺寸（原圖 80%），centre=False 是隨機位置
    o_flip_lr,              # 左右翻轉
    o_flip_tb,              # 上下翻轉
    o_flip_random,          # 左右、上下、不翻 隨機選一個
    o_rotate_90,            # 隨機轉 90 / 180 / 270 度，-1 是隨機選，也可以固定寫 90、180、270
    o_rotate_range,         # 任意角度旋轉，左右各最多 15 度（範圍 0 到 25），會裁掉黑邊
    o_rotate_standard,      # 任意角度旋轉，左右各最多 15 度（範圍 0 到 25），expand=False 不擴大畫布
    o_skew_tilt,            # 透視傾斜（上下左右選一邊），magnitude 範圍 0 到 1
    o_skew_corner,          # 透視拉一個角，magnitude 範圍 0 到 1
    o_shear,                # 剪切，左右各最多 10 度（範圍 0 到 25）
    o_scale,                # 等比放大 1.2 倍，範圍 1 以上，畫面會變大
    o_zoom,                 # 放大後裁回原尺寸，倍數 1.0 到 1.3
    o_zoom_random,          # 隨機放大，保留 80% 面積，randomise 是面積也隨機
    o_crop_percentage,      # 依面積百分比裁切，80% 面積，位置和面積都隨機
    o_crop_random,          # 隨機位置裁切 80% 面積
    o_distort,              # 格子扭曲，格數 4x4，magnitude 越大越歪
    o_gaussian_distortion,  # 高斯扭曲，corner=bell 是中心凸起，method=in 是往內
    o_resize,               # 縮成固定尺寸（原圖一半），輸出尺寸會變
]  # 圖和 mask 一起轉的幾何轉換；o_crop 固定尺寸要放最前面、o_resize 放最後，不然尺寸被前面的轉換改掉會報錯

o_brightness = Augmentor.Operations.RandomBrightness(probability=0.5, min_factor=0.8, max_factor=1.2)                                                      # 亮度乘 0.8 到 1.2 倍
o_color = Augmentor.Operations.RandomColor(probability=0.3, min_factor=0.8, max_factor=1.2)                                                                # 飽和度乘 0.8 到 1.2 倍
o_contrast = Augmentor.Operations.RandomContrast(probability=0.3, min_factor=0.8, max_factor=1.2)                                                          # 對比乘 0.8 到 1.2 倍
o_histogram = Augmentor.Operations.HistogramEqualisation(probability=0.3)                                                                                  # 直方圖均衡化
o_greyscale = Augmentor.Operations.Greyscale(probability=0.3)                                                                                              # 轉灰階
o_invert = Augmentor.Operations.Invert(probability=0.3)                                                                                                    # 顏色反相
o_black_and_white = Augmentor.Operations.BlackAndWhite(probability=0.3, threshold=128)                                                                     # 二值化，threshold 範圍 0 到 255
o_hsv = Augmentor.Operations.HSVShifting(probability=0.3, hue_shift=0.05, saturation_scale=0.2, saturation_shift=0.05, value_scale=0.2, value_shift=0.05)  # HSV 位移，hue_shift 範圍 0 到 0.5
o_erasing = Augmentor.Operations.RandomErasing(probability=0.3, rectangle_area=0.2)                                                                        # 隨機遮擋一塊雜訊，面積範圍 0 到 1

l_color = [
    o_brightness,       # 亮度乘 0.8 到 1.2 倍
    o_color,            # 飽和度乘 0.8 到 1.2 倍
    o_contrast,         # 對比乘 0.8 到 1.2 倍
    o_histogram,        # 直方圖均衡化
    o_greyscale,        # 轉灰階
    o_invert,           # 顏色反相
    o_black_and_white,  # 二值化，threshold 範圍 0 到 255
    o_hsv,              # HSV 位移，hue_shift 範圍 0 到 0.5
    o_erasing,          # 隨機遮擋一塊雜訊，面積範圍 0 到 1
]  # 只轉圖的色彩轉換

# 各轉換的 probability 是觸發機率，0 是不用，1 是每張都做
os.makedirs("runtime/output", exist_ok=True)
for i_index in range(50):
    l_images = [o_image] + l_masks
    for o_operation in l_geometry:
        if random.random() < o_operation.probability:
            l_images = o_operation.perform_operation(l_images)
    l_image = [l_images[0]]
    for o_operation in l_color:
        if random.random() < o_operation.probability:
            l_image = o_operation.perform_operation(l_image)
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
