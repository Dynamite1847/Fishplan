"""Add height dimensions to the actual FreeCAD side projection."""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def mark_section(run):
    drawing = Image.open(run / '围挡右视底图.png').convert('RGB')
    camera = json.loads((run / '侧剖相机.json').read_text())
    geometry = json.loads((run / '围挡建模结果.json').read_text())
    width, height = drawing.size
    scale = height / camera['height_mm']
    _, center_y, center_z = camera['center']
    ink = '#183541'
    gray = '#526b76'
    green = '#147c78'
    font_path = '/System/Library/Fonts/Hiragino Sans GB.ttc'
    canvas = ImageDraw.Draw(drawing)

    def point(y, z):
        return (round(width / 2 + (y - center_y) * scale), round(height / 2 - (z - center_z) * scale))

    def write(x, y, text, size=27, color=ink, bold=False, anchor='la'):
        font = ImageFont.truetype(font_path, size, index=int(bold))
        canvas.text((x, y), text, fill=color, font=font, anchor=anchor)

    def line(*points, color=gray, line_width=2):
        canvas.line(points, fill=color, width=line_width)

    panel_height = geometry['panel_top_above_rim_mm']
    lamp_height = geometry['lamp_top_above_rim_mm']
    panel_x, panel_top = point(2, 500 + panel_height)
    _, rim = point(2, 500)
    lamp_x, lamp_top = point(105, 500 + lamp_height)
    dimension_x = panel_x - 82
    for screen_y in (panel_top, rim):
        line((dimension_x - 9, screen_y), (panel_x - 9, screen_y), color=green)
    line((dimension_x, panel_top), (dimension_x, rim), color=green, line_width=3)
    write(dimension_x - 13, (panel_top + rim) // 2, f'{panel_height} mm', 31, green, True, 'rm')
    write(dimension_x - 13, (panel_top + rim) // 2 + 40, '含座安装高', 23, gray, anchor='rm')

    label_y = panel_top - 118
    line((lamp_x + 120, lamp_top - 3), (lamp_x + 120, label_y + 73), color=green)
    write(lamp_x + 120, label_y, 'L290 低位灯顶', 26, green, True, 'ma')
    write(lamp_x + 120, label_y + 35, f'低于板沿 {panel_height - lamp_height:g} mm', 25, gray, anchor='ma')

    write(105, 86, '主缸围挡 · 内藏风扇与灯体', 39, bold=True)
    write(105, 146, '移去两侧板显示内部灯体、遮光罩及后置风扇', 27, gray)
    write(105, height - 91, '缸沿上 202 mm；前板含 14 mm 下裙；灯顶按 +180 mm 包络。', 24, gray)
    drawing.save(run / '围挡右视.png', optimize=True)


if __name__ == '__main__':
    mark_section(Path(sys.argv[1]))
