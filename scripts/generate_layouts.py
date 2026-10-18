"""Generate concept diagrams and geometric comparisons; not fabrication drawings."""

from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design"
OUT.mkdir(exist_ok=True)

FONT = "'PingFang SC','Microsoft YaHei',sans-serif"
NAVY = "#17324d"
BLUE = "#147dba"
GREEN = "#23866e"
RED = "#c64c52"
GOLD = "#aa7414"


class SVG:
    def __init__(self, width, height, title, desc):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<title>{escape(title)}</title><desc>{escape(desc)}</desc>',
            f'<rect width="{width}" height="{height}" fill="#f4f7fa"/>',
            '<defs>',
        ]
        for name, color in [("blue", BLUE), ("green", GREEN), ("red", RED), ("gold", GOLD)]:
            self.parts.append(f'<marker id="{name}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="{color}"/></marker>')
        self.parts.append('</defs>')

    def rect(self, x, y, w, h, fill, stroke="none", sw=1, radius=0):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, value, size=20, color=NAVY, weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def path(self, d, color, width=3, arrow=None, dashed=False):
        opts = f' marker-end="url(#{arrow})"' if arrow else ""
        if dashed:
            opts += ' stroke-dasharray="9 6"'
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{opts}/>')

    def save(self, name):
        (OUT / name).write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")


cases = []
for depth in (400, 450):
    sump_depth = depth - 120
    sump_inner_length = 400 - 12
    sump_inner_depth = sump_depth - 12
    area = sump_inner_length * sump_inner_depth
    display_upper_backflow = 600 * depth * 20 / 1e6
    reserve = area * (350 - 200) / 1e6
    cases.append({
        "depth_mm": depth,
        "display_outer_mm": [600, depth, 400],
        "display_gross_l": 600 * depth * 400 / 1e6,
        "display_water_before_displacement_l": 584 * (depth - 16) * 350 / 1e6,
        "frame_concept_outer_mm": [600, depth, 800],
        "frame_geometric_inner_plan_mm": [520, depth - 80],
        "sump_concept_outer_mm": [400, sump_depth, 400],
        "sump_assumed_inner_plan_mm": [sump_inner_length, sump_inner_depth],
        "sump_geometric_water_at_200mm_l": area * 200 / 1e6,
        "sump_geometric_reserve_200_to_350mm_l": reserve,
        "display_20mm_drawdown_outer_area_upper_estimate_l": display_upper_backflow,
        "illustrative_budget_l": {
            "additional_overflow_and_pipe_backflow": 2,
            "ato_volume_case_1": 3,
            "ato_volume_case_2": 5,
            "extra_margin": 3,
        },
        "illustrative_remaining_reserve_with_3l_ato_l": reserve - display_upper_backflow - 2 - 3 - 3,
        "illustrative_remaining_reserve_with_5l_ato_l": reserve - display_upper_backflow - 2 - 5 - 3,
    })
    # Simple dimensional checks for the drawn placeholders, not structural checks.
    assert 400 < 520 and sump_depth < depth - 80
    assert reserve > 0

(OUT / "容量估算-v0.1.json").write_text(json.dumps({
    "status": "concept only; not validated safety capacity or structural design",
    "units": {"dimensions": "mm", "volume": "L"},
    "assumptions": [
        "Display wall/bottom 8mm and sump wall/bottom 6mm are calculation assumptions, not glass specifications.",
        "Display water depth 350mm; sump operating depth 200mm; provisional sump maximum safe depth 350mm, measured from inside bottom.",
        "Assumes all sump compartments can use the calculated reserve; ignores equipment and pipe displacement.",
        "2L extra backflow, 3L/5L ATO and 3L additional margin are examples, not engineered or verified requirements.",
        "Cabinet panel thickness, fittings, clearances and structural requirements remain unresolved.",
    ],
    "cases": cases,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


svg = SVG(1400, 1400, "60×40与60×45底滤海缸概念布局比较", "两版使用相同平面比例。展示缸、架内底缸、补水位置和几何余量。非加工图。")
svg.text(45, 55, "Fishplan · 两版总体布局", 32, weight=700)
svg.text(45, 91, "v0.1 / 2026-10-18 · 单位mm · 概念占位图，不能据此下料、开孔或采购", 19, color="#62748a")

scale = 0.78
for index, case in enumerate(cases):
    left = 35 + index * 675
    x = left + 65
    depth = case["depth_mm"]
    svg.rect(left, 115, 650, 1150, "white", "#dfe7ee", radius=14)
    svg.text(left + 25, 158, f'{"A" if index == 0 else "B"} · 600 × {depth}', 28, weight=700)
    svg.text(left + 25, 192, "40深优先方案" if index == 0 else "适度扩深方案（候选优先）", 21, color=BLUE)
    svg.text(x, 236, "主缸俯视 · 上方为后墙", 20, weight=600)
    y = 264
    svg.rect(x, y, 600 * scale, depth * scale, "#eaf7fc", BLUE, 3)
    # Overflow footprint is a placeholder only; no hole geometry is implied.
    svg.rect(x + 6, y + 6, 190 * scale, 100 * scale, "#d9e2ea", "#9cafbf", 1)
    svg.text(x + 80, y + 38, "溢流占位", 17, anchor="middle")
    svg.text(x + 80, y + 63, "尺寸待定", 16, color="#62748a", anchor="middle")
    svg.text(x + 265, y + depth * scale * 0.58, "展示 / 造景空间", 23, anchor="middle")
    svg.text(x + 265, y + depth * scale * 0.58 + 32, "珊瑚、海葵留生长间距", 17, color="#62748a", anchor="middle")
    svg.text(x + 235, y + depth * scale + 30, "正面：主要观赏与维护", 18, anchor="middle")
    svg.text(x - 10, y + depth * scale * 0.58, "左", 17, anchor="end")
    svg.text(x - 10, y + depth * scale * 0.58 + 24, "过道", 17, anchor="end")
    svg.text(x + 480, y + depth * scale * 0.58, "右侧", 17)
    svg.text(x + 480, y + depth * scale * 0.58 + 24, "电视柜", 17)
    svg.text(x, 665, "架内俯视 · 同比例", 20, weight=600)
    y = 690
    svg.rect(x, y, 600 * scale, depth * scale, "#cbd6df", NAVY, 2)
    svg.rect(x + 40 * scale, y + 40 * scale, 520 * scale, (depth - 80) * scale, "#fff")
    svg.rect(x + 45 * scale, y + 45 * scale, 510 * scale, (depth - 90) * scale, "#fff9e8", "#d4b364", 1)
    svg.rect(x + 50 * scale, y + 55 * scale, 400 * scale, (depth - 120) * scale, "#dff3ee", GREEN, 2)
    center_y = y + depth * scale / 2
    svg.text(x + 250 * scale, center_y - 10, "底缸占位", 22, color=GREEN, weight=600, anchor="middle")
    svg.text(x + 250 * scale, center_y + 22, f'400 × {depth - 120} × 400高', 18, color=GREEN, anchor="middle")
    svg.text(x + 250 * scale, center_y + 50, "分仓 / 设备 / 水位待选型", 16, color="#62748a", anchor="middle")
    svg.rect(x + 460 * scale, y + 80 * scale, 90 * scale, 225 * scale, "#fff0c6", GOLD, 2, radius=4)
    svg.text(x + 505 * scale, y + 145 * scale, "补水", 17, color=GOLD, anchor="middle")
    svg.text(x + 505 * scale, y + 175 * scale, "容器", 17, color=GOLD, anchor="middle")
    svg.text(x + 505 * scale, y + 205 * scale, "占位", 17, color=GOLD, anchor="middle")
    svg.text(x + 230, y + depth * scale + 30, "黄色底层：接水盘占位；尚未核对成品规格", 16, color=GOLD, anchor="middle")
    svg.text(left + 25, 1120, f'架内几何净空：520 × {depth - 80}', 21, weight=600)
    svg.text(left + 25, 1156, f'底缸账面余量：{case["sump_geometric_reserve_200_to_350mm_l"]:.1f} L', 22, color=GREEN, weight=600)
    svg.text(left + 25, 1188, "按水深200→350估算，未扣设备占容", 18, color="#62748a")
    svg.text(left + 25, 1222, "净空未扣角件、管件及施工余量", 18, color="#62748a")

svg.text(45, 1305, "两版架高均以800为起点；主缸400高只用于比较。面板后装，接口及厚度须提前协调。", 19)
svg.text(45, 1340, "窄补水容器、接水盘、溢流区均为占位，未确认在售或可加工；图中容量不是安全认证。", 19, color=RED)
svg.save("布局比较-v0.1.svg")


svg = SVG(1200, 1200, "DIY底滤海缸系统水路示意", "主缸、独立主下水及应急下水、底缸回水、有限补水容器、接水和配电位置的示意，非比例加工图。")
svg.text(45, 55, "Fishplan · 系统水路", 32, weight=700)
svg.text(45, 91, "v0.1 · 两个尺寸方案共用的结构思路 / 非比例示意，孔位、分仓和管径未定", 19, color="#62748a")
svg.rect(145, 145, 720, 245, "#eaf7fc", BLUE, 3)
svg.rect(165, 155, 145, 225, "#e0e7ed", "#9cafbf", 2)
svg.text(590, 235, "主缸", 29, weight=600, anchor="middle")
svg.text(590, 275, "600 × 400 / 450 · 高度待定", 22, anchor="middle")
svg.text(590, 310, "展示空间与溢流占位需联合核对", 18, color="#62748a", anchor="middle")
svg.text(237, 188, "溢流区", 20, anchor="middle")
svg.path("M 315 210 L 175 210", BLUE, 3, arrow="blue")
svg.rect(130, 410, 750, 580, "#fff", "#9cafbf", 12)
svg.text(500, 455, "铝架：约800高 · 正面保持可检修", 21, anchor="middle")
svg.rect(180, 650, 525, 255, "#eef8f4", GREEN, 3)
svg.rect(183, 785, 519, 117, "#cdece3")
svg.path("M 185 700 L 700 700", RED, 2, dashed=True)
svg.path("M 185 785 L 700 785", BLUE, 2, dashed=True)
svg.text(450, 684, "预留容水空间", 23, color=GREEN, weight=600, anchor="middle")
svg.text(450, 731, "最高安全水位：待核算与测试", 18, color=RED, anchor="middle")
svg.text(450, 773, "运行水位：随设备确认", 18, color=BLUE, anchor="middle")
svg.text(255, 855, "物理过滤", 19, anchor="middle")
svg.text(435, 855, "蛋分 / 设备", 19, anchor="middle")
svg.text(625, 855, "回水", 19, anchor="middle")
svg.path("M 300 820 L 365 820", GREEN, 3, arrow="green")
svg.path("M 495 820 L 565 820", GREEN, 3, arrow="green")
svg.path("M 205 240 L 205 615 L 235 615 L 235 805", GREEN, 5, arrow="green")
svg.text(65, 535, "主下水", 19, color=GREEN)
svg.text(65, 562, "设调节", 17, color=GREEN)
svg.path("M 270 215 L 270 590 L 310 590 L 310 805", RED, 4, arrow="red", dashed=True)
svg.text(310, 515, "独立应急下水", 19, color=RED)
svg.text(310, 545, "主下水异常时承担排水", 17, color=RED)
svg.path("M 650 820 L 720 820 L 720 600 L 845 600 L 845 125 L 790 125 L 790 200", BLUE, 5, arrow="blue")
svg.text(885, 340, "回水", 19, color=BLUE)
svg.text(885, 375, "回水口位置", 17, color=BLUE)
svg.text(885, 402, "决定反虹吸量", 17, color=BLUE)
svg.rect(750, 680, 80, 225, "#fff0c6", GOLD, 2, radius=6)
svg.text(790, 737, "有限", 19, color=GOLD, anchor="middle")
svg.text(790, 767, "补水", 19, color=GOLD, anchor="middle")
svg.text(790, 797, "容器", 19, color=GOLD, anchor="middle")
svg.path("M 790 850 L 790 630 L 610 630 L 610 750", GOLD, 3, arrow="gold")
svg.text(335, 625, "补水管：固定出口并处理虹吸", 17, color=GOLD)
svg.rect(685, 475, 155, 105, "#edf1f5", "#9cafbf", 2, radius=6)
svg.text(762, 515, "配电 / 控制器", 18, anchor="middle")
svg.text(762, 546, "干燥高位待布局", 16, color="#62748a", anchor="middle")
svg.rect(160, 925, 690, 35, "#fff4d6", GOLD, 2)
svg.text(505, 950, "接水盘 + 漏水检测；容量及联动待设计", 18, color=GOLD, anchor="middle")
svg.text(45, 1035, "① 停泵：底缸接住回流水　② 堵管：独立应急下水接流量", 22, weight=600)
svg.text(45, 1075, "③ 误补水：限量 + 保护　④ 漏水：接水、检测及经验证的停机", 22, weight=600)
svg.text(45, 1125, "图仅解释水路与功能位置，不代表缸架结构、玻璃孔位或设备已经兼容。", 19, color=RED)
svg.save("系统水路-v0.1.svg")

for case in cases:
    print(f'{case["depth_mm"]}mm depth: geometric sump reserve {case["sump_geometric_reserve_200_to_350mm_l"]:.1f}L')
print("Generated two SVG diagrams and the geometric calculation JSON; concept only.")
