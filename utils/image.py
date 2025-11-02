from PIL import Image

def resize_and_crop(image_path, output_path, size=(800, 600), crop=True):
    """
    调整图片大小并可裁剪
    :param image_path: 原图片路径
    :param output_path: 输出图片路径
    :param size: (width, height) 目标尺寸
    :param crop: True -> 裁剪图片以填充目标尺寸
                 False -> 仅缩放，可能留白
    """
    img = Image.open(image_path)
    original_width, original_height = img.size
    target_width, target_height = size

    if crop:
        # 计算缩放比例，保证图片覆盖整个目标区域
        ratio = max(target_width / original_width, target_height / original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        img = img.resize(new_size, Image.ANTIALIAS)

        # 裁剪中心部分
        left = (new_size[0] - target_width) / 2
        top = (new_size[1] - target_height) / 2
        right = left + target_width
        bottom = top + target_height
        img = img.crop((left, top, right, bottom))
    else:
        # 仅缩放，不裁剪
        img = img.resize(size, Image.Resampling.LANCZOS)

    img.save(output_path)
    print(f"✅ 图片已保存到: {output_path}")
