# -*- coding: utf-8 -*-
import os


def get_icon_path(icon_name):
    icons_dir = "/".join(
        __file__.replace("\\", "/").split("/")[:-2] + ["resources", "icons"]
    )
    for name in os.listdir(icons_dir):
        if name == icon_name:
            return os.path.join(icons_dir, icon_name).replace("\\", "/")
