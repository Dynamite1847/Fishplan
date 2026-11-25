"""样稿用的鱼抠图：从高清原始透明 PNG 裁掉透明边、统一朝右、导出 webp。

在 Fishplan 根目录运行：python3 资料/交付/网页设计预览/Claude样稿/处理抠图.py 输出目录
"""
import os
import sys

from PIL import Image, ImageOps

SRC = "资料/参考图/鱼抠图"
FLIP = {"bisp", "para", "tomi"}  # 原图鱼头朝左的，镜像成朝右
MAX_W = 1400

out = sys.argv[1] if len(sys.argv) > 1 else "资料/交付/网页设计预览/Claude样稿/img"
os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".png"):
        continue
    key = f.split("-")[0]
    im = Image.open(os.path.join(SRC, f)).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 24 else 0).getbbox())
    if key in FLIP:
        im = ImageOps.mirror(im)
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(os.path.join(out, f"{key}.webp"), "WEBP", quality=88, method=6)
    print(key, im.size)
