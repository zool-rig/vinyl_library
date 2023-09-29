# -*- coding: utf-8 -*-
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from frontend.lib.icons import get_icon_path


def make_icon(icon_name):
    icon_path = get_icon_path(icon_name)
    return QIcon(icon_path) if icon_path else None


def make_tool_button(icon_name, tooltip="", checkable=False):
    btn = QToolButton()
    icon = make_icon(icon_name)
    if icon:
        btn.setIcon(icon)
    btn.setToolTip(tooltip)
    btn.setCheckable(checkable)
    return btn


def get_image_average_pixel_color(img: QImage, step=1):
    if any((not img.width(), not img.height())):
        return tuple()

    color_map = [[], [], []]
    pixel_count = 0

    for x, y in zip(range(0, img.width(), step), range(0, img.height(), step)):
        pixel_color = img.pixelColor(x, y)
        if any(
            (
                (pixel_color.red(), pixel_color.green(), pixel_color.blue()) == (255, 255, 255),
                (pixel_color.red(), pixel_color.green(), pixel_color.blue()) == (0, 0, 0),
            )
        ):
            continue
        color_map[0].append(pixel_color.red())
        color_map[1].append(pixel_color.green())
        color_map[2].append(pixel_color.blue())
        pixel_count += 1

    if not pixel_count:
        return 0, 0, 0

    return (
        (sum(color_map[0]) / pixel_count),
        (sum(color_map[1]) / pixel_count),
        (sum(color_map[2]) / pixel_count)
    )

