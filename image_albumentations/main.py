import json
import os

import albumentations
import albumentations.augmentations.geometric.functional
import albumentations.core.bbox_utils
import cv2
import numpy

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


o_random_resized_crop = albumentations.RandomResizedCrop(size=(720, 1280), scale=(0.5, 1.0), p=0.3)                                     # 隨機裁切一塊（面積 50% 到 100%）再縮回 720x1280
o_random_sized_crop = albumentations.RandomSizedCrop(min_max_height=(400, 576), size=(720, 1280), w2h_ratio=1280 / 720, p=0.3)          # 隨機高度 400 到 576 的裁切，再縮回 720x1280
o_random_sized_bbox_safe_crop = albumentations.RandomSizedBBoxSafeCrop(height=720, width=1280, p=0.3)                                  # 隨機裁切但不會切到框，再縮回 720x1280
o_random_crop = albumentations.RandomCrop(height=576, width=1024, p=0.3)                                                                # 隨機位置裁成 576x1024
o_center_crop = albumentations.CenterCrop(height=576, width=1024, p=0.3)                                                                # 中心裁成 576x1024
o_crop = albumentations.Crop(x_min=0, y_min=0, x_max=1024, y_max=576, p=0.3)                                                            # 固定區域裁切，左上角 1024x576
o_at_least_one_bbox_random_crop = albumentations.AtLeastOneBBoxRandomCrop(height=576, width=1024, p=0.3)                               # 隨機裁成 576x1024，至少包含一個框
o_bbox_safe_random_crop = albumentations.BBoxSafeRandomCrop(p=0.3)                                                                     # 隨機裁切，不會切到框，輸出尺寸會變
o_random_crop_from_borders = albumentations.RandomCropFromBorders(p=0.3)                                                                # 四邊各隨機裁掉最多 10%（crop_left、crop_right、crop_top、crop_bottom）
o_crop_and_pad = albumentations.CropAndPad(percent=(-0.1, 0.1), p=0.3)                                                                  # 負值裁切、正值補黑邊，最多 10%，補完縮回原尺寸
o_horizontal_flip = albumentations.HorizontalFlip(p=0.5)                                                                                # 左右翻轉
o_vertical_flip = albumentations.VerticalFlip(p=0.3)                                                                                    # 上下翻轉
o_transpose = albumentations.Transpose(p=0.3)                                                                                           # 對角線翻轉（長寬互換）
o_random_rotate90 = albumentations.RandomRotate90(p=0.3)                                                                                # 隨機轉 90 / 180 / 270 度
o_d4 = albumentations.D4(p=0.3)                                                                                                         # 8 種翻轉加 90 度旋轉的組合隨機選一種
o_square_symmetry = albumentations.SquareSymmetry(p=0.3)                                                                                # 正方形的 8 種對稱隨機選一種，跟 D4 效果一樣
o_rotate = albumentations.Rotate(limit=15, p=0.5)                                                                                       # 旋轉，角度範圍 -15 到 15 度
o_safe_rotate = albumentations.SafeRotate(limit=15, p=0.3)                                                                              # 旋轉，會縮小畫面讓整張圖留在畫面內
o_affine = albumentations.Affine(scale=(0.9, 1.1), translate_percent=(-0.1, 0.1), rotate=(-15, 15), shear=(-10, 10), p=0.3)             # 縮放、平移、旋轉、傾斜一起做
o_perspective = albumentations.Perspective(scale=(0.05, 0.1), p=0.3)                                                                    # 透視變形，scale 越大越歪
o_piecewise_affine = albumentations.PiecewiseAffine(scale=(0.01, 0.03), p=0)                                                            # 局部扭曲，很慢而且框可能不準，所以預設不用
o_elastic_transform = albumentations.ElasticTransform(alpha=1, sigma=50, p=0.3)                                                         # 彈性扭曲，框可能不準
o_grid_distortion = albumentations.GridDistortion(num_steps=5, distort_limit=0.3, p=0.3)                                                # 格子扭曲，框可能不準
o_grid_elastic_deform = albumentations.GridElasticDeform(num_grid_xy=(4, 4), magnitude=10, p=0.3)                                       # 格子彈性變形，框可能不準
o_optical_distortion = albumentations.OpticalDistortion(distort_limit=0.05, p=0.3)                                                      # 鏡頭桶狀 / 枕狀扭曲
o_thin_plate_spline = albumentations.ThinPlateSpline(scale_range=(0.2, 0.4), p=0.3)                                                     # 薄板樣條變形，框可能不準
o_random_grid_shuffle = albumentations.RandomGridShuffle(grid=(3, 3), p=0.3)                                                            # 把圖切成 3x3 格再隨機打亂位置
o_coarse_dropout = albumentations.CoarseDropout(p=0.3)                                                                                  # 隨機挖掉幾個方塊（num_holes_range、hole_height_range、hole_width_range）
o_constrained_coarse_dropout = albumentations.ConstrainedCoarseDropout(p=0.3)                                                           # 挖掉方塊，位置限制在框內
o_grid_dropout = albumentations.GridDropout(ratio=0.5, p=0.3)                                                                           # 依格子規律挖洞，ratio 是洞佔格子的比例
o_pixel_dropout = albumentations.PixelDropout(dropout_prob=0.01, p=0.3)                                                                 # 隨機把 1% 的像素設成 0
o_xy_masking = albumentations.XYMasking(num_masks_x=(1, 2), num_masks_y=(1, 2), mask_x_length=(20, 60), mask_y_length=(20, 60), p=0.3)  # 隨機畫幾條橫線和直線遮住
o_erasing = albumentations.Erasing(scale=(0.02, 0.33), p=0.3)                                                                           # 隨機擦掉一塊，scale 是面積比例
o_morphological = MorphologicalPerBox(scale=(2, 3), operation="dilation", p=0.3)                                               # 形態學膨脹（dilation）或侵蝕（erosion）
o_pad = albumentations.Pad(padding=20, p=0.3)                                                                                           # 四邊補 20 像素黑邊
o_pad_if_needed = albumentations.PadIfNeeded(min_height=800, min_width=1400, p=0.3)                                                     # 畫面小於 800x1400 就補黑邊到這個尺寸
o_random_scale = albumentations.RandomScale(scale_limit=0.1, p=0.3)                                                                     # 縮放 ±10%，輸出尺寸會變
o_resize = albumentations.Resize(height=360, width=640, p=0.3)                                                                          # 縮成 360x640
o_longest_max_size = albumentations.LongestMaxSize(max_size=800, p=0.3)                                                                 # 最長邊縮到 800，等比
o_smallest_max_size = albumentations.SmallestMaxSize(max_size=400, p=0.3)                                                               # 最短邊縮到 400，等比
o_random_brightness_contrast = albumentations.RandomBrightnessContrast(p=0.5)                                                           # 亮度、對比（brightness_limit、contrast_limit 預設 ±0.2）
o_random_gamma = albumentations.RandomGamma(gamma_limit=(80, 120), p=0.3)                                                               # Gamma 80 到 120，小於 100 變亮、大於 100 變暗
o_random_tone_curve = albumentations.RandomToneCurve(scale=0.1, p=0.3)                                                                  # 隨機扭曲色調曲線
o_clahe = albumentations.CLAHE(clip_limit=4.0, p=0.3)                                                                                   # 局部對比增強
o_equalize = albumentations.Equalize(p=0.3)                                                                                             # 直方圖均衡化
o_auto_contrast = albumentations.AutoContrast(p=0.3)                                                                                    # 自動對比，拉伸到最大範圍
o_illumination = albumentations.Illumination(p=0.3)                                                                                     # 模擬光線（線性、圓形、角落）
o_plasma_brightness_contrast = albumentations.PlasmaBrightnessContrast(p=0.3)                                                           # 用雲狀圖樣局部改亮度對比
o_plasma_shadow = albumentations.PlasmaShadow(p=0.3)                                                                                    # 用雲狀圖樣加陰影
o_color_jitter = albumentations.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.02, p=0.3)                              # 亮度、對比、飽和度、色相抖動，hue 範圍 0 到 0.5
o_hue_saturation_value = albumentations.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=20, p=0.3)           # 色相、飽和度、明度位移
o_rgb_shift = albumentations.RGBShift(r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, p=0.3)                                      # R、G、B 各通道位移
o_planckian_jitter = albumentations.PlanckianJitter(p=0.3)                                                                              # 模擬色溫變化（偏黃到偏藍）
o_channel_shuffle = albumentations.ChannelShuffle(p=0.3)                                                                                # R、G、B 通道隨機換位
o_channel_dropout = albumentations.ChannelDropout(p=0.3)                                                                                # 隨機丟掉一個通道
o_to_gray = albumentations.ToGray(p=0.3)                                                                                                # 轉灰階
o_to_sepia = albumentations.ToSepia(p=0.3)                                                                                              # 轉懷舊棕褐色
o_invert_img = albumentations.InvertImg(p=0.3)                                                                                          # 顏色反相
o_solarize = albumentations.Solarize(p=0.3)                                                                                             # 曝光過度，亮部反相
o_posterize = albumentations.Posterize(p=0.3)                                                                                           # 減少色階（色調分離）
o_fancy_pca = albumentations.FancyPCA(p=0.3)                                                                                            # 沿主成分方向改色（AlexNet 的作法）
o_blur = albumentations.Blur(blur_limit=7, p=0.3)                                                                                       # 平均模糊，核大小 3 到 7
o_gaussian_blur = albumentations.GaussianBlur(blur_limit=(3, 7), p=0.3)                                                                 # 高斯模糊，核大小 3 到 7
o_median_blur = albumentations.MedianBlur(blur_limit=5, p=0.3)                                                                          # 中值模糊，核大小 3 到 5
o_motion_blur = albumentations.MotionBlur(blur_limit=7, p=0.3)                                                                          # 動態模糊
o_advanced_blur = albumentations.AdvancedBlur(p=0.3)                                                                                    # 進階模糊（橢圓核、旋轉）
o_defocus = albumentations.Defocus(p=0.3)                                                                                               # 失焦模糊
o_zoom_blur = albumentations.ZoomBlur(p=0.3)                                                                                            # 放射狀的縮放模糊
o_glass_blur = albumentations.GlassBlur(p=0)                                                                                            # 玻璃模糊，非常慢所以預設不用
o_sharpen = albumentations.Sharpen(p=0.3)                                                                                               # 銳化
o_unsharp_mask = albumentations.UnsharpMask(p=0.3)                                                                                      # 反銳化遮罩，增強邊緣
o_emboss = albumentations.Emboss(p=0.3)                                                                                                 # 浮雕
o_ringing_overshoot = albumentations.RingingOvershoot(p=0.3)                                                                            # 模擬過衝（邊緣振鈴）失真
o_superpixels = albumentations.Superpixels(p=0)                                                                                         # 超像素，非常慢所以預設不用
o_gauss_noise = albumentations.GaussNoise(p=0.5)                                                                                        # 高斯雜訊
o_additive_noise = albumentations.AdditiveNoise(p=0.3)                                                                                  # 加法雜訊（均勻、高斯、拉普拉斯、beta 擇一）
o_multiplicative_noise = albumentations.MultiplicativeNoise(multiplier=(0.9, 1.1), p=0.3)                                               # 乘法雜訊，像素各乘 0.9 到 1.1
o_iso_noise = albumentations.ISONoise(p=0.3)                                                                                            # 模擬感光度（ISO）雜訊
o_shot_noise = albumentations.ShotNoise(p=0.3)                                                                                          # 光子散粒雜訊
o_salt_and_pepper = albumentations.SaltAndPepper(p=0.3)                                                                                 # 椒鹽雜訊
o_image_compression = albumentations.ImageCompression(p=0.3)                                                                            # JPEG / WebP 壓縮失真
o_downscale = albumentations.Downscale(p=0.3)                                                                                           # 縮小再放大，變模糊
o_chromatic_aberration = albumentations.ChromaticAberration(p=0.3)                                                                      # 色差，邊緣紅藍偏移
o_random_fog = albumentations.RandomFog(p=0.3)                                                                                          # 霧
o_random_rain = albumentations.RandomRain(p=0.3)                                                                                        # 雨
o_random_snow = albumentations.RandomSnow(p=0.3)                                                                                        # 雪
o_random_shadow = albumentations.RandomShadow(p=0.3)                                                                                    # 隨機陰影
o_random_sun_flare = albumentations.RandomSunFlare(p=0.3)                                                                               # 太陽光暈
o_random_gravel = albumentations.RandomGravel(p=0.3)                                                                                    # 路面碎石顆粒
o_spatter = albumentations.Spatter(p=0.3)                                                                                               # 泥點、水滴噴濺

# 各轉換的 p 是觸發機率，0 是不用，1 是每張都做；固定尺寸的裁切放最前面、改尺寸的放最後，不然尺寸被前面的轉換改掉會報錯
o_transform = albumentations.Compose(
    [
        o_random_resized_crop,
        o_random_sized_crop,
        o_random_sized_bbox_safe_crop,
        o_random_crop,
        o_center_crop,
        o_crop,
        o_at_least_one_bbox_random_crop,
        o_bbox_safe_random_crop,
        o_random_crop_from_borders,
        o_crop_and_pad,
        o_horizontal_flip,
        o_vertical_flip,
        o_transpose,
        o_random_rotate90,
        o_d4,
        o_square_symmetry,
        o_rotate,
        o_safe_rotate,
        o_affine,
        o_perspective,
        o_piecewise_affine,
        o_elastic_transform,
        o_grid_distortion,
        o_grid_elastic_deform,
        o_optical_distortion,
        o_thin_plate_spline,
        o_random_grid_shuffle,
        o_coarse_dropout,
        o_constrained_coarse_dropout,
        o_grid_dropout,
        o_pixel_dropout,
        o_xy_masking,
        o_erasing,
        o_morphological,
        o_pad,
        o_pad_if_needed,
        o_random_scale,
        o_resize,
        o_longest_max_size,
        o_smallest_max_size,
        o_random_brightness_contrast,
        o_random_gamma,
        o_random_tone_curve,
        o_clahe,
        o_equalize,
        o_auto_contrast,
        o_illumination,
        o_plasma_brightness_contrast,
        o_plasma_shadow,
        o_color_jitter,
        o_hue_saturation_value,
        o_rgb_shift,
        o_planckian_jitter,
        o_channel_shuffle,
        o_channel_dropout,
        o_to_gray,
        o_to_sepia,
        o_invert_img,
        o_solarize,
        o_posterize,
        o_fancy_pca,
        o_blur,
        o_gaussian_blur,
        o_median_blur,
        o_motion_blur,
        o_advanced_blur,
        o_defocus,
        o_zoom_blur,
        o_glass_blur,
        o_sharpen,
        o_unsharp_mask,
        o_emboss,
        o_ringing_overshoot,
        o_superpixels,
        o_gauss_noise,
        o_additive_noise,
        o_multiplicative_noise,
        o_iso_noise,
        o_shot_noise,
        o_salt_and_pepper,
        o_image_compression,
        o_downscale,
        o_chromatic_aberration,
        o_random_fog,
        o_random_rain,
        o_random_snow,
        o_random_shadow,
        o_random_sun_flare,
        o_random_gravel,
        o_spatter,
    ],
    bbox_params=albumentations.BboxParams(format="pascal_voc", label_fields=["l_labels"]),
)

os.makedirs("runtime/output", exist_ok=True)
for i_index in range(50):
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
