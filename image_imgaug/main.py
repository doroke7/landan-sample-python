import json
import os

import cv2
import imgaug.augmentables.bbs
import imgaug.augmenters
import numpy

numpy.complex = complex  # imgaug 用到 np.complex / np.bool，NumPy 1.24 之後移除了，補回別名
numpy.bool = bool

s_name = "2026-08-09@036"
a_image = cv2.imread(f"runtime/raw/{s_name}.png")
with open(f"runtime/raw/{s_name}.json") as o_file:
    d_label = json.load(o_file)

l_boxes = []
for d_shape in d_label["shapes"]:
    l_xs = [l_point[0] for l_point in d_shape["points"]]
    l_ys = [l_point[1] for l_point in d_shape["points"]]
    f_x1 = min(l_xs)
    f_y1 = min(l_ys)
    f_x2 = max(l_xs)
    f_y2 = max(l_ys)
    l_boxes.append(imgaug.augmentables.bbs.BoundingBox(x1=f_x1, y1=f_y1, x2=f_x2, y2=f_y2, label=d_shape["label"]))
o_boxes = imgaug.augmentables.bbs.BoundingBoxesOnImage(l_boxes, shape=a_image.shape)

o_fliplr = imgaug.augmenters.Fliplr(0.5)                                                                                 # 左右翻轉，機率 0.5
o_flipud = imgaug.augmenters.Flipud(0.5)                                                                                 # 上下翻轉，機率 0.5
o_rot90 = imgaug.augmenters.Rot90((1, 3))                                                                                # 轉 90 / 180 / 270 度，長寬不同會被拉伸
o_affine = imgaug.augmenters.Affine(rotate=(-15, 15), scale=(0.8, 1.2), translate_percent=(-0.1, 0.1), shear=(-10, 10))  # 旋轉 ±15 度、縮放 0.8 到 1.2 倍、平移 ±10%、傾斜 ±10 度
o_perspective = imgaug.augmenters.PerspectiveTransform(scale=(0.01, 0.1))                                                # 透視變形，scale 越大越歪
o_crop = imgaug.augmenters.Crop(percent=(0, 0.1))                                                                        # 四邊各隨機裁掉 0 到 10%，裁完會放大回原尺寸
o_crop_and_pad = imgaug.augmenters.CropAndPad(percent=(-0.1, 0.1), pad_mode="constant", pad_cval=0)                      # 負值裁切、正值補黑邊，最多 10%，補完縮回原尺寸
o_piecewise_affine = imgaug.augmenters.PiecewiseAffine(scale=(0.01, 0.03))                                               # 局部扭曲，框會不準
o_elastic = imgaug.augmenters.ElasticTransformation(alpha=(0, 30), sigma=5)                                              # 彈性扭曲，框會不準
o_multiply = imgaug.augmenters.Multiply((0.8, 1.2))                                                                      # 亮度乘 0.8 到 1.2 倍
o_add_brightness = imgaug.augmenters.AddToBrightness((-30, 30))                                                          # 亮度加減 -30 到 30
o_multiply_brightness = imgaug.augmenters.MultiplyBrightness((0.8, 1.2))                                                 # 亮度乘 0.8 到 1.2 倍（HSV 的 V 通道）
o_contrast = imgaug.augmenters.LinearContrast((0.75, 1.5))                                                               # 對比乘 0.75 到 1.5 倍
o_gamma = imgaug.augmenters.GammaContrast((0.7, 1.5))                                                                    # Gamma 對比，小於 1 變亮、大於 1 變暗
o_clahe = imgaug.augmenters.CLAHE(clip_limit=(1, 4))                                                                     # 局部對比增強
o_saturation = imgaug.augmenters.MultiplySaturation((0.7, 1.3))                                                          # 飽和度乘 0.7 到 1.3 倍
o_hue = imgaug.augmenters.AddToHue((-10, 10))                                                                            # 色相加減 -10 到 10（範圍 -255 到 255）
o_hue_saturation = imgaug.augmenters.MultiplyHueAndSaturation(mul_saturation=(0.7, 1.3))                                 # 同時調色相和飽和度
o_grayscale = imgaug.augmenters.Grayscale(alpha=(0.0, 1.0))                                                              # 轉灰階，alpha 是混合比例
o_temperature = imgaug.augmenters.ChangeColorTemperature((4000, 9000))                                                   # 色溫（K），小偏黃、大偏藍
o_gaussian_blur = imgaug.augmenters.GaussianBlur(sigma=(0, 2.0))                                                         # 高斯模糊，sigma 越大越糊
o_motion_blur = imgaug.augmenters.MotionBlur(k=7)                                                                        # 動態模糊，k 是模糊長度
o_average_blur = imgaug.augmenters.AverageBlur(k=(2, 5))                                                                 # 平均模糊，k 是核大小
o_median_blur = imgaug.augmenters.MedianBlur(k=(3, 5))                                                                   # 中值模糊，k 要是奇數
o_gaussian_noise = imgaug.augmenters.AdditiveGaussianNoise(scale=(0, 10))                                                # 高斯雜訊，scale 是標準差（0 到 255）
o_laplace_noise = imgaug.augmenters.AdditiveLaplaceNoise(scale=(0, 10))                                                  # 拉普拉斯雜訊
o_poisson_noise = imgaug.augmenters.AdditivePoissonNoise(lam=(0, 10))                                                    # 泊松雜訊
o_salt_and_pepper = imgaug.augmenters.SaltAndPepper(0.01)                                                                # 椒鹽雜訊，1% 的像素
o_dropout = imgaug.augmenters.Dropout(p=(0, 0.05))                                                                       # 隨機把像素設成黑
o_coarse_dropout = imgaug.augmenters.CoarseDropout(p=(0.02, 0.1), size_percent=(0.02, 0.05))                             # 隨機遮擋小方塊
o_jpeg = imgaug.augmenters.JpegCompression(compression=(70, 95))                                                         # JPEG 壓縮失真，數字越大壓縮越狠
o_fog = imgaug.augmenters.Fog()                                                                                          # 霧
o_clouds = imgaug.augmenters.Clouds()                                                                                    # 雲
o_snow = imgaug.augmenters.Snowflakes()                                                                                  # 雪花
o_rain = imgaug.augmenters.Rain()                                                                                        # 雨

# Sometimes(機率, 轉換)：機率 0 是不用，1 是每張都做；機率可以直接改下面的數字
o_transform = imgaug.augmenters.Sequential([
    o_fliplr,
    imgaug.augmenters.Sometimes(0.5, o_flipud),             # 上下翻轉
    imgaug.augmenters.Sometimes(0.5, o_rot90),                # 轉 90 / 180 / 270 度
    imgaug.augmenters.Sometimes(0.5, o_affine),             # 旋轉 ±15 度、縮放 0.8 到 1.2 倍、平移 ±10%、傾斜 ±10 度
    imgaug.augmenters.Sometimes(0.2, o_perspective),        # 透視變形
    imgaug.augmenters.Sometimes(0.2, o_crop),               # 四邊各隨機裁掉 0 到 10%
    imgaug.augmenters.Sometimes(0.5, o_crop_and_pad),         # 負值裁切、正值補黑邊
    imgaug.augmenters.Sometimes(0, o_piecewise_affine),     # 局部扭曲
    imgaug.augmenters.Sometimes(0.5, o_elastic),              # 彈性扭曲
    imgaug.augmenters.Sometimes(0.5, o_multiply),           # 亮度乘 0.8 到 1.2 倍
    imgaug.augmenters.Sometimes(0.5, o_add_brightness),       # 亮度加減 -30 到 30
    imgaug.augmenters.Sometimes(0.5, o_multiply_brightness),  # 亮度乘 0.8 到 1.2 倍（HSV 的 V 通道）
    imgaug.augmenters.Sometimes(0.5, o_contrast),           # 對比乘 0.75 到 1.5 倍
    imgaug.augmenters.Sometimes(0.2, o_gamma),              # Gamma 對比
    imgaug.augmenters.Sometimes(0.5, o_clahe),                # 局部對比增強
    imgaug.augmenters.Sometimes(0.3, o_saturation),         # 飽和度乘 0.7 到 1.3 倍
    imgaug.augmenters.Sometimes(0.1, o_hue),                # 色相加減 -10 到 10（範圍 -255 到 255）
    imgaug.augmenters.Sometimes(0.5, o_hue_saturation),       # 同時調色相和飽和度
    imgaug.augmenters.Sometimes(0.5, o_grayscale),            # 轉灰階
    imgaug.augmenters.Sometimes(0.1, o_temperature),        # 色溫（K）
    imgaug.augmenters.Sometimes(0.2, o_gaussian_blur),      # 高斯模糊
    imgaug.augmenters.Sometimes(0.2, o_motion_blur),        # 動態模糊
    imgaug.augmenters.Sometimes(0.5, o_average_blur),         # 平均模糊
    imgaug.augmenters.Sometimes(0.5, o_median_blur),          # 中值模糊
    imgaug.augmenters.Sometimes(0.5, o_gaussian_noise),     # 高斯雜訊
    imgaug.augmenters.Sometimes(0.5, o_laplace_noise),        # 拉普拉斯雜訊
    imgaug.augmenters.Sometimes(0.5, o_poisson_noise),        # 泊松雜訊
    imgaug.augmenters.Sometimes(0.5, o_salt_and_pepper),      # 椒鹽雜訊
    imgaug.augmenters.Sometimes(0.5, o_dropout),              # 隨機把像素設成黑
    imgaug.augmenters.Sometimes(0.1, o_coarse_dropout),     # 隨機遮擋小方塊
    imgaug.augmenters.Sometimes(0.1, o_jpeg),               # JPEG 壓縮失真
    imgaug.augmenters.Sometimes(0.5, o_fog),                  # 霧
    imgaug.augmenters.Sometimes(0.5, o_clouds),               # 雲
    imgaug.augmenters.Sometimes(0.5, o_snow),                 # 雪花
    imgaug.augmenters.Sometimes(0.5, o_rain),                 # 雨
])

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(50):
    a_output, o_out_boxes = o_transform(image=a_image, bounding_boxes=o_boxes)
    o_out_boxes = o_out_boxes.clip_out_of_image()
    cv2.imwrite(f"runtime/output/{i_index}.png", a_output)

    l_shapes = []
    for o_box in o_out_boxes.bounding_boxes:
        l_points = [[float(o_box.x1), float(o_box.y1)], [float(o_box.x2), float(o_box.y2)]]
        l_shapes.append({"label": o_box.label, "points": l_points, "group_id": None, "shape_type": "rectangle", "flags": {}})
    d_output = dict(d_label)
    d_output["shapes"] = l_shapes
    d_output["imagePath"] = f"{i_index}.png"
    with open(f"runtime/output/{i_index}.json", "w") as o_file:
        json.dump(d_output, o_file, ensure_ascii=False, indent=2)
