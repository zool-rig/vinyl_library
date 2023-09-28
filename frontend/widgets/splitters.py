from PySide6.QtWidgets import QFrame


class HSplitter(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setObjectName("Splitter")


class VSplitter(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.VLine)
        self.setObjectName("Splitter")
