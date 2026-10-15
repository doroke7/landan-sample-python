import json
import os

import kornia.augmentation
import torch
import torchvision.io
import torchvision.utils

s_name = "2026-08-09@036"
a_uint8 = torchvision.io.read_image(f"runtime/raw/{s_name}.png")
a_image = a_uint8.float().unsqueeze(0) / 255
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

def skip_empty_batch(o_augmentation):  # Kornia 的 bug：p 小於 1 又沒被選中時，會拿空的 batch 去產生參數而報 Invalid input tensor, it is empty
    f_generate = o_augmentation.generate_parameters
    def generate(o_batch_shape):
        if o_batch_shape[0] == 0:  # 這一輪沒被選中，不用產生參數
            return {}
        return f_generate(o_batch_shape)
    o_augmentation.generate_parameters = generate
    return o_augmentation

o_random_resized_crop = kornia.augmentation.RandomResizedCrop(size=(720, 1280), scale=(0.5, 1.0), p=0.3)                                       # 隨機裁切一塊（面積 50% 到 100%）再縮回 720x1280
o_random_crop = kornia.augmentation.RandomCrop(size=(576, 1024), pad_if_needed=True, p=0.3)                                                    # 隨機位置裁成 576x1024，畫面比較小就先補邊
o_center_crop = kornia.augmentation.CenterCrop(size=(576, 1024), p=0.3)                                                                        # 中心裁成 576x1024
o_random_horizontal_flip = kornia.augmentation.RandomHorizontalFlip(p=0.5)                                                                     # 左右翻轉
o_random_vertical_flip = kornia.augmentation.RandomVerticalFlip(p=0.3)                                                                         # 上下翻轉
o_random_rotation = kornia.augmentation.RandomRotation(degrees=20, resample="BILINEAR", p=0.3)                                                 # 旋轉 -20 到 20 度，resample 是插值方式
o_random_rotation90 = kornia.augmentation.RandomRotation90(times=(1, 3), p=0.3)                                                                # 轉 90 度的 1 到 3 倍（90 / 180 / 270 度）
o_random_affine = kornia.augmentation.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1), shear=10, p=0.3)                        # 旋轉、平移 ±10%、縮放 0.9 到 1.1 倍、傾斜 ±10 度一起做
o_random_shear = kornia.augmentation.RandomShear(shear=10, p=0.3)                                                                              # 傾斜 -10 到 10 度
o_random_translate = kornia.augmentation.RandomTranslate(translate_x=(-0.1, 0.1), translate_y=(-0.1, 0.1), p=0.3)                              # 左右、上下平移 ±10%
o_random_perspective = kornia.augmentation.RandomPerspective(distortion_scale=0.15, sampling_method="area_preserving", p=0.3)                  # 透視變形，area_preserving 黑邊較少
o_color_jitter = kornia.augmentation.ColorJitter(brightness=(0.7, 1.3), contrast=(0.7, 1.3), saturation=(0.7, 1.3), hue=(-0.03, 0.03), p=0.5)  # 亮度、對比、飽和度 0.7 到 1.3 倍，色相 ±0.03
o_color_jiggle = kornia.augmentation.ColorJiggle(brightness=(0.7, 1.3), contrast=(0.7, 1.3), saturation=(0.7, 1.3), hue=(-0.03, 0.03), p=0.3)  # 同 ColorJitter，差別是 ColorJiggle 的四個調整依固定順序做
o_random_brightness = kornia.augmentation.RandomBrightness(brightness=(0.7, 1.3), p=0.3)                                                       # 亮度乘 0.7 到 1.3 倍
o_random_contrast = kornia.augmentation.RandomContrast(contrast=(0.7, 1.3), p=0.3)                                                             # 對比乘 0.7 到 1.3 倍
o_random_saturation = kornia.augmentation.RandomSaturation(saturation=(0.7, 1.3), p=0.3)                                                       # 飽和度乘 0.7 到 1.3 倍
o_random_hue = kornia.augmentation.RandomHue(hue=(-0.03, 0.03), p=0.3)                                                                         # 色相位移，範圍 -0.5 到 0.5
o_random_gamma = kornia.augmentation.RandomGamma(gamma=(0.7, 1.5), p=0.3)                                                                      # Gamma，小於 1 變亮、大於 1 變暗
o_random_auto_contrast = kornia.augmentation.RandomAutoContrast(p=0.3)                                                                         # 自動對比
o_random_equalize = kornia.augmentation.RandomEqualize(p=0.3)                                                                                  # 直方圖均衡化
o_random_clahe = kornia.augmentation.RandomClahe(clip_limit=(2.0, 4.0), p=0.3)                                                                 # 局部對比增強
o_random_grayscale = kornia.augmentation.RandomGrayscale(p=0.3)                                                                                # 轉灰階（還是 3 個通道）
o_random_invert = kornia.augmentation.RandomInvert(p=0.3)                                                                                      # 顏色反相
o_random_posterize = kornia.augmentation.RandomPosterize(bits=3, p=0.3)                                                                        # 減少色階，bits 範圍 0 到 8
o_random_solarize = kornia.augmentation.RandomSolarize(thresholds=0.1, additions=0.1, p=0.3)                                                   # 曝光過度，高於門檻的像素反相
o_random_sharpness = kornia.augmentation.RandomSharpness(sharpness=0.5, p=0.3)                                                                 # 銳化，數值越大越銳利
o_random_channel_shuffle = kornia.augmentation.RandomChannelShuffle(p=0.3)                                                                     # R、G、B 通道隨機換位
o_random_channel_dropout = kornia.augmentation.RandomChannelDropout(num_drop_channels=1, p=0.3)                                                # 隨機丟掉 1 個通道（補 0）
o_random_rgb_shift = kornia.augmentation.RandomRGBShift(r_shift_limit=0.1, g_shift_limit=0.1, b_shift_limit=0.1, p=0.3)                        # R、G、B 各通道位移，範圍 0 到 1
o_random_planckian_jitter = kornia.augmentation.RandomPlanckianJitter(p=0.3)                                                                   # 模擬色溫變化（偏黃到偏藍）
o_random_plasma_brightness = kornia.augmentation.RandomPlasmaBrightness(p=0.3)                                                                 # 用雲狀圖樣局部改亮度
o_random_plasma_contrast = kornia.augmentation.RandomPlasmaContrast(p=0.3)                                                                     # 用雲狀圖樣局部改對比
o_random_plasma_shadow = kornia.augmentation.RandomPlasmaShadow(p=0.3)                                                                         # 用雲狀圖樣加陰影
o_random_linear_illumination = kornia.augmentation.RandomLinearIllumination(p=0.3)                                                             # 線性光照，一邊亮一邊暗
o_random_linear_corner_illumination = kornia.augmentation.RandomLinearCornerIllumination(p=0.3)                                                # 從角落打光
o_random_gaussian_illumination = kornia.augmentation.RandomGaussianIllumination(p=0.3)                                                         # 高斯光斑，局部變亮或變暗
o_random_gaussian_blur = kornia.augmentation.RandomGaussianBlur(kernel_size=(7, 7), sigma=(0.1, 1.5), border_type="reflect", p=0.3)            # 高斯模糊，邊緣鏡射補齊
o_random_box_blur = kornia.augmentation.RandomBoxBlur(kernel_size=(3, 3), p=0.3)                                                               # 平均模糊
o_random_median_blur = kornia.augmentation.RandomMedianBlur(kernel_size=(3, 3), p=0.3)                                                         # 中值模糊
o_random_motion_blur = kornia.augmentation.RandomMotionBlur(kernel_size=7, angle=35.0, direction=0.5, p=0.3)                                   # 動態模糊，angle 是方向角度，direction 範圍 -1 到 1
o_random_gaussian_noise = kornia.augmentation.RandomGaussianNoise(mean=0.0, std=0.05, p=0.3)                                                   # 高斯雜訊，std 以 0 到 1 的像素值為基準
o_random_salt_and_pepper_noise = kornia.augmentation.RandomSaltAndPepperNoise(p=0.3)                                                           # 椒鹽雜訊
o_random_jpeg = kornia.augmentation.RandomJPEG(jpeg_quality=(50.0, 95.0), p=0.3)                                                               # JPEG 壓縮失真，quality 範圍 0 到 100
o_random_rain = kornia.augmentation.RandomRain(p=0.3)                                                                                          # 雨
o_random_snow = kornia.augmentation.RandomSnow(p=0.3)                                                                                          # 雪
o_random_erasing = kornia.augmentation.RandomErasing(scale=(0.02, 0.1), p=0.3)                                                                 # 隨機擦掉一塊，scale 是面積比例
o_resize = kornia.augmentation.Resize(size=(360, 640), side="short", p=0.3)                                                                    # 縮成 360x640
o_longest_max_size = kornia.augmentation.LongestMaxSize(max_size=800, p=0.3)                                                                   # 最長邊縮到 800，等比
o_smallest_max_size = kornia.augmentation.SmallestMaxSize(max_size=400, p=0.3)                                                                 # 最短邊縮到 400，等比

o_random_gaussian_illumination = skip_empty_batch(o_random_gaussian_illumination)
o_random_linear_corner_illumination = skip_empty_batch(o_random_linear_corner_illumination)

# 各轉換的 p 是觸發機率，0 是不用，1 是每張都做；固定尺寸的裁切放最前面、改尺寸的放最後，不然尺寸被前面的轉換改掉會報錯
l_augmentations = [
    o_random_resized_crop,
    o_random_crop,
    o_center_crop,
    o_random_horizontal_flip,
    o_random_vertical_flip,
    o_random_rotation,
    o_random_rotation90,
    o_random_affine,
    o_random_shear,
    o_random_translate,
    o_random_perspective,
    o_color_jitter,
    o_color_jiggle,
    o_random_brightness,
    o_random_contrast,
    o_random_saturation,
    o_random_hue,
    o_random_gamma,
    o_random_auto_contrast,
    o_random_equalize,
    o_random_clahe,
    o_random_grayscale,
    o_random_invert,
    o_random_posterize,
    o_random_solarize,
    o_random_sharpness,
    o_random_channel_shuffle,
    o_random_channel_dropout,
    o_random_rgb_shift,
    o_random_planckian_jitter,
    o_random_plasma_brightness,
    o_random_plasma_contrast,
    o_random_plasma_shadow,
    o_random_linear_illumination,
    o_random_linear_corner_illumination,
    o_random_gaussian_illumination,
    o_random_gaussian_blur,
    o_random_box_blur,
    o_random_median_blur,
    o_random_motion_blur,
    o_random_gaussian_noise,
    o_random_salt_and_pepper_noise,
    o_random_jpeg,
    o_random_rain,
    o_random_snow,
    o_random_erasing,
    o_resize,
    o_longest_max_size,
    o_smallest_max_size,
]
o_transform = kornia.augmentation.AugmentationSequential(*l_augmentations, data_keys=["input", "bbox_xyxy"])  # bbox_xyxy 讓框跟圖一起轉

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(50):
    a_output, a_out_boxes = o_transform(a_image, a_boxes)
    torchvision.utils.save_image(a_output, f"runtime/output/{i_index}.png")

    i_out_height, i_out_width = a_output.shape[-2:]  # 有些轉換會改尺寸，框要貼合輸出圖的大小
    l_shapes = []
    for l_bbox, s_label in zip(a_out_boxes[0].tolist(), l_labels):
        f_x1 = max(l_bbox[0], 0)
        f_y1 = max(l_bbox[1], 0)
        f_x2 = min(l_bbox[2], i_out_width)
        f_y2 = min(l_bbox[3], i_out_height)
        if f_x2 - f_x1 < 1 or f_y2 - f_y1 < 1:
            continue
        l_points = [[f_x1, f_y1], [f_x2, f_y2]]
        l_shapes.append({"label": s_label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
