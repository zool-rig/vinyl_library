# -*- coding: utf-8 -*-
import re
import time
from functools import partial

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from frontend.api import VinylLibraryAPI, Artist
from frontend.dialogs import EditVinylDialog, ShuffleVinylsDialog
from frontend.lib.utils import make_tool_button, make_icon
from frontend.widgets import *


class VinylLibraryUI(QDialog):
    class SortingModes(object):
        DATE = 0
        ARTISTS = 1
        VINYLS = 2
        LABELS = (
            "Recently added",
            "Artists (A-Z)",
            "Vinyl (A-Z)",
        )

    class DisplayModes(object):
        MOSAIC = 0
        LIST = 1

    def __init__(self):
        super().__init__()
        self.api = VinylLibraryAPI()
        self.current_sorting_mode = self.SortingModes.DATE
        self.current_display_mode = self.DisplayModes.MOSAIC
        self.vinyl_name_filter = str()
        self.artists_filter = set()

        # Layouts
        self.main_h_layout = None
        self.toolbar_v_layout = None
        self.artists_v_layout = None
        self.vinyls_v_layout = None
        self.header_h_layout = None
        self.scroll_area_v_layout = None
        self.mosaic_layout = None
        self.list_layout = None

        # Widgets
        self.add_vinyl_btn = None
        self.toggle_artists_btn = None
        self.shuffle_btn = None
        self.artists_splitter = None
        self.artists_lbl = None
        self.artists_list = None
        self.vinyl_count_lbl = None
        self.vinyl_search_bar = None
        self.sorting_cbx = None
        self.display_mosaic_btn = None
        self.display_list_btn = None
        self.scroll_area = None
        self.scroll_area_widget = None
        self.vinyl_widgets = list()

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()
        self.fill_vinyls()
        self.fill_artists()

    def init_layouts(self):
        self.main_h_layout = QHBoxLayout(self)
        self.toolbar_v_layout = QVBoxLayout()
        self.artists_v_layout = QVBoxLayout()
        self.vinyls_v_layout = QVBoxLayout()
        self.header_h_layout = QHBoxLayout()
        self.scroll_area_v_layout = QVBoxLayout()
        self.mosaic_layout = FlowLayout()
        self.list_layout = QVBoxLayout()

    def init_widgets(self):
        self.add_vinyl_btn = make_tool_button("add.png", tooltip="Add vinyl")
        self.toggle_artists_btn = make_tool_button(
            "artist.png", tooltip="Toggle artists list", checkable=True
        )
        self.shuffle_btn = make_tool_button("shuffle.png", tooltip="Shuffle")
        self.artists_splitter = VSplitter()
        self.artists_lbl = QLabel()
        self.artists_list = QListWidget()
        self.vinyl_count_lbl = QLabel()
        self.vinyl_search_bar = QLineEdit()
        self.sorting_cbx = QComboBox()
        self.display_mosaic_btn = make_tool_button(
            "mosaic.png", tooltip="Display mosaic", checkable=True
        )
        self.display_list_btn = make_tool_button(
            "list.png", tooltip="Display list", checkable=True
        )
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()

    def set_layouts(self):
        self.main_h_layout.addLayout(self.toolbar_v_layout)
        self.toolbar_v_layout.addWidget(self.add_vinyl_btn)
        self.toolbar_v_layout.addWidget(self.toggle_artists_btn)
        self.toolbar_v_layout.addWidget(self.shuffle_btn)
        self.main_h_layout.addWidget(self.artists_splitter)
        self.main_h_layout.addLayout(self.artists_v_layout)
        self.artists_v_layout.addWidget(self.artists_lbl)
        self.artists_v_layout.addWidget(self.artists_list)
        self.main_h_layout.addWidget(VSplitter())
        self.main_h_layout.addLayout(self.vinyls_v_layout)
        self.vinyls_v_layout.addLayout(self.header_h_layout)
        self.header_h_layout.addWidget(self.vinyl_count_lbl)
        self.header_h_layout.addStretch()
        self.header_h_layout.addWidget(self.vinyl_search_bar)
        self.header_h_layout.addStretch()
        self.header_h_layout.addWidget(self.sorting_cbx)
        self.header_h_layout.addWidget(self.display_mosaic_btn)
        self.header_h_layout.addWidget(self.display_list_btn)
        self.vinyls_v_layout.addWidget(HSplitter())
        self.vinyls_v_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area_widget.setLayout(self.scroll_area_v_layout)
        self.scroll_area_v_layout.addLayout(self.mosaic_layout)
        self.scroll_area_v_layout.addLayout(self.list_layout)

    def set_connections(self):
        self.add_vinyl_btn.clicked.connect(self.add_vinyl)
        self.toggle_artists_btn.toggled.connect(self.toggle_artists_widgets)
        self.artists_list.itemSelectionChanged.connect(self.set_artist_filter)
        self.shuffle_btn.clicked.connect(self.shuffle_vinyls)
        self.vinyl_search_bar.textChanged.connect(self.set_vinyl_filter)
        self.sorting_cbx.currentIndexChanged.connect(self.set_sorting_mode)
        self.display_mosaic_btn.clicked.connect(
            lambda: self.set_display_mode(
                self.DisplayModes.MOSAIC, self.display_mosaic_btn.isChecked()
            )
        )
        self.display_list_btn.clicked.connect(
            lambda: self.set_display_mode(
                self.DisplayModes.LIST, self.display_list_btn.isChecked()
            )
        )
        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self.process_visible_vinyl_widgets
        )

    def set_default(self):
        self.setWindowTitle("Vinyl Library")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        for layout, alignment in (
            (self.toolbar_v_layout, Qt.AlignTop),
            (self.artists_v_layout, Qt.AlignTop),
            (self.vinyls_v_layout, Qt.AlignTop),
            (self.list_layout, Qt.AlignTop),
        ):
            layout.setAlignment(alignment)
        self.toggle_artists_widgets(False)
        self.update_artists_count()
        self.artists_lbl.setFont(QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 18))
        self.artists_list.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.MinimumExpanding
        )
        self.artists_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.artists_list.setMinimumWidth(200)
        self.artists_list.installEventFilter(self)
        self.vinyl_search_bar.setPlaceholderText("🔍\tSearch vinyls")
        self.vinyl_search_bar.setObjectName("SearchBar")
        self.vinyl_search_bar.setMinimumWidth(350)
        self.update_vinyls_count()
        self.vinyl_count_lbl.setFont(
            QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 18)
        )
        self.sorting_cbx.addItems(self.SortingModes.LABELS)
        self.display_mosaic_btn.setChecked(True)
        self.scroll_area.setWidgetResizable(True)

    def show(self, *args, **kwargs):
        self.init_ui()
        super().show(*args, **kwargs)
        self.run_deferred(self.process_visible_vinyl_widgets)

    def showEvent(self, arg__1):
        self.resize(855, 595)

    def eventFilter(self, widget, event):
        if widget == self.artists_list and event.type() == QEvent.ContextMenu:
            self.show_artist_list_context_menu(self.mapToGlobal(event.pos()))
        return super().eventFilter(widget, event)

    def vinyl_sorter(self, vinyl):
        return {
            self.SortingModes.DATE: time.time() - vinyl.added_date,
            self.SortingModes.ARTISTS: vinyl.artist_name,
            self.SortingModes.VINYLS: vinyl.name,
        }.get(self.current_sorting_mode)

    def fill_vinyls(self):
        for widget in self.vinyl_widgets:
            widget.deleteLater()
        self.vinyl_widgets = list()
        for vinyl in sorted(self.api.vinyls, key=self.vinyl_sorter):
            layout, widget_class = {
                self.DisplayModes.MOSAIC: (self.mosaic_layout, VinylMosaicWidget),
                self.DisplayModes.LIST: (self.list_layout, VinylListWidget),
            }.get(self.current_display_mode)
            widget = widget_class(vinyl)
            widget.edit_requested.connect(partial(self.edit_vinyl))
            widget.delete_requested.connect(partial(self.delete_vinyl_with_prompt))
            widget.listen_requested.connect(partial(self.api.listen_vinyl))
            layout.addWidget(widget)
            self.vinyl_widgets.append(widget)

    def set_display_mode(self, mode, state):
        other_button, other_mode = {
            self.DisplayModes.MOSAIC: (self.display_list_btn, self.DisplayModes.LIST),
            self.DisplayModes.LIST: (self.display_mosaic_btn, self.DisplayModes.MOSAIC),
        }.get(mode)
        other_button.setChecked(not state)
        self.current_display_mode = mode if state else other_mode
        self.fill_vinyls()
        self.run_deferred(self.process_visible_vinyl_widgets)

    def set_sorting_mode(self, mode):
        self.current_sorting_mode = mode
        self.fill_vinyls()
        self.run_deferred(self.process_visible_vinyl_widgets)

    def toggle_artists_widgets(self, state):
        for widget in (
            self.artists_splitter,
            self.artists_lbl,
            self.artists_list,
        ):
            widget.setVisible(state)
        if not state:
            self.artists_list.clearSelection()

    def add_artist_item_to_list(self, artist):
        item = QListWidgetItem(artist.pretty_name)
        setattr(item, "artist", artist)
        self.artists_list.addItem(item)

    def fill_artists(self):
        self.artists_list.clear()
        for artist in self.api.artists:
            self.add_artist_item_to_list(artist)

    def filter_vinyls(self):
        for vinyl_widget in self.vinyl_widgets:
            if (
                self.vinyl_name_filter
                and re.search(self.vinyl_name_filter, vinyl_widget.vinyl.name) is None
            ):
                vinyl_widget.setHidden(True)
                continue
            if (
                self.artists_filter
                and vinyl_widget.vinyl.artist_id not in self.artists_filter
            ):
                vinyl_widget.setHidden(True)
                continue
            vinyl_widget.setVisible(True)
        self.run_deferred(self.process_visible_vinyl_widgets)

    def set_vinyl_filter(self, pattern):
        try:
            self.vinyl_name_filter = re.compile(pattern)
        except re.error:
            self.vinyl_name_filter = None
        self.filter_vinyls()

    def set_artist_filter(self):
        self.artists_filter = [
            item.artist.id for item in self.artists_list.selectedItems()
        ]
        self.filter_vinyls()

    def add_vinyl(self):
        dialog = EditVinylDialog(self, self.api)
        ok, vinyl_data = dialog.exec()
        if not ok:
            return

        new_artist, do_update_artists_list = self.api.add_artist(
            vinyl_data["artist_name"]
        )
        if do_update_artists_list:
            self.add_artist_item_to_list(new_artist)
            self.update_artists_count()

        new_vinyl, do_update_vinyls = self.api.add_vinyl(
            vinyl_data["vinyl_name"],
            new_artist.id,
            new_artist.name,
            vinyl_data["cover_file_name"],
        )
        if do_update_vinyls:
            self.update_vinyls_count()
            self.fill_vinyls()
            self.process_visible_vinyl_widgets()

    def update_artists_count(self):
        self.artists_lbl.setText(f"{len(self.api.artists)} Artists")

    def update_vinyls_count(self):
        self.vinyl_count_lbl.setText(f"{len(self.api.vinyls)} Vinyls")

    @staticmethod
    def run_deferred(func, delay=0, *args, **kwargs):
        QTimer.singleShot(delay, lambda: func(*args, **kwargs))

    def process_visible_vinyl_widgets(self):
        viewport_geo = self.scroll_area.viewport().geometry()
        scroll_value = self.scroll_area.verticalScrollBar().value()
        for widget in self.vinyl_widgets:
            if widget.is_loaded:
                continue
            widget_geometry = widget.geometry()
            widget_geometry.translate(0, -scroll_value)
            if viewport_geo.intersects(widget_geometry):
                widget.load(self.api.get_image(widget.vinyl.cover_file_name))

    def resizeEvent(self, event):
        self.run_deferred(self.process_visible_vinyl_widgets)
        return super().resizeEvent(event)

    def edit_vinyl(self, widget):
        current_data = {
            "artist_name": widget.vinyl.artist_name,
            "cover_file_name": widget.vinyl.cover_file_name,
            "vinyl_name": widget.vinyl.name,
        }
        dialog = EditVinylDialog(self, self.api, **current_data)
        ok, vinyl_data = dialog.exec()
        if not ok or vinyl_data == current_data:
            return

        artist = self.api.find_artist_by_name(vinyl_data["artist_name"])
        if artist is None:
            artist, _ = self.api.add_artist(vinyl_data["artist_name"])

        vinyl = self.api.update_vinyl(
            widget.vinyl.id,
            vinyl_data["vinyl_name"],
            artist.id,
            artist.name,
            vinyl_data["cover_file_name"],
        )

        widget.update_vinyl(vinyl, self.api.get_image(vinyl.cover_file_name))

    def delete_vinyl(self, widget):
        self.api.delete_vinyl(widget.vinyl)
        self.vinyl_widgets.remove(widget)
        widget.deleteLater()
        self.update_vinyls_count()
        self.run_deferred(self.process_visible_vinyl_widgets)

    def delete_vinyl_with_prompt(self, widget):
        do_it = QMessageBox.question(
            self,
            "Delete Vinyl",
            f"Are you sure you want to delete {widget.vinyl.artist_pretty_name}'s {widget.vinyl.pretty_name} ?",
        )
        if do_it == QMessageBox.No:
            return

        artist = Artist(widget.vinyl.artist_id, widget.vinyl.artist_name)
        self.delete_vinyl(widget)

        if not self.api.get_vinyls_for_artist(artist):
            do_it = QMessageBox.question(
                self,
                "Delete Artist",
                f"the artist {artist.pretty_name} has no more vinyls, would you like to delete it ?",
            )
            if do_it == QMessageBox.Yes:
                self.delete_artist(artist)

    def delete_artist(self, artist):
        for i in range(self.artists_list.count()):
            item = self.artists_list.item(i)
            if item.artist == artist:
                self.artists_list.takeItem(i)
                break
        self.api.delete_artist(artist)
        self.api.artists.remove(artist)

    def delete_artist_with_prompt(self, artist):
        related_vinyls = self.api.get_vinyls_for_artist(artist)
        if related_vinyls:
            do_it = QMessageBox.question(
                self,
                "Delete Artist and related vinyls",
                f"Are you sure you want to delete {artist.pretty_name} ?"
                f"\nThere is {len(related_vinyls)} related vinyls that will be deleted to",
            )
            if do_it == QMessageBox.No:
                return

            to_delete = list()
            for widget in self.vinyl_widgets:
                if widget.vinyl in related_vinyls:
                    to_delete.append(widget)

            for widget in to_delete:
                self.delete_vinyl(widget)

        self.delete_artist(artist)

    def show_artist_list_context_menu(self, pos):
        selected_items = self.artists_list.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        menu = QMenu()
        rename_action = menu.addAction("Rename")
        rename_action.setIcon(make_icon("edit.png"))
        rename_action.triggered.connect(lambda: self.rename_artist(selected_item))
        delete_action = menu.addAction("Delete")
        delete_action.setIcon(make_icon("delete.png"))
        delete_action.triggered.connect(lambda: self.delete_artist_with_prompt(selected_item.artist))
        menu.exec(pos)

    def rename_artist(self, item):
        user_input = QInputDialog.getText(self, "Rename artist", "New name :")
        if not all(user_input):
            return

        new_name, _ = user_input
        item.artist = self.api.update_artist(item.artist, new_name)
        item.setText(item.artist.pretty_name)

        related_vinyls_ids = {vinyl.id for vinyl in self.api.get_vinyls_for_artist(item.artist)}
        for widget in self.vinyl_widgets:
            if widget.vinyl.id in related_vinyls_ids:
                widget.vinyl.artist_name = item.artist.name
                widget.artist_lbl.setText(item.artist.pretty_name)

    def shuffle_vinyls(self):
        ShuffleVinylsDialog(self).exec()


if __name__ == "__main__":
    import sys
    app = QApplication([])
    ui = VinylLibraryUI()
    ui.show()
    style_file = r"C:\python_projects\vinyl_library\frontend\resources\style\style.qss"
    with open(style_file, "r") as f:
        ui.setStyleSheet(f.read())
    sys.exit(app.exec())
