from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")



def style_sheet() -> str:
    return """
        QMainWindow { background: #000000; }
        QWidget { color: #eef8ff; font-size: 10.5pt; }
        QLabel#Title { color: #ffffff; }
        QLabel#Subtitle { color: #b8d5dd; }
        QLabel#SubtitleSmall { color: #7fa3ae; font-size: 9.5pt; }
        QLabel#PathLabel { color: #8fb4bf; background: rgba(0, 0, 0, 150); border: 1px solid rgba(40, 223, 219, 100); padding: 7px; border-radius: 6px; }
        QFrame#TopLogoBar { background: transparent; border: none; }
        QLabel#TopLogoLabel { background: transparent; border: none; }
        QFrame#RightShell { background: transparent; border: none; }
        QFrame#StructureSettingsBlankPanel { background: transparent; border: none; }
        QTabWidget#MainTabs::pane { border: 1px solid rgba(40, 200, 214, 115); border-radius: 10px; background: rgba(2, 8, 12, 88); top: -1px; }
        QTabBar::tab { background: rgba(4, 10, 14, 150); color: #86a7b1; border: 1px solid rgba(48, 82, 97, 150); border-bottom: none; padding: 10px 18px; margin-right: 4px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 700; }
        QTabBar::tab:selected { background: rgba(6, 16, 22, 210); color: #ffffff; border-color: rgba(37, 234, 215, 180); }
        QTabBar::tab:hover { background: rgba(8, 20, 28, 190); color: #eef8ff; border-color: rgba(37, 234, 215, 120); }
        QWidget#GridContainer { background: rgba(3, 10, 14, 115); border: 1px solid rgba(45, 187, 204, 105); border-radius: 10px; }
        QLabel#HeaderLabel { color: #ffffff; font-weight: 700; }
        QLabel#AreaLabel { color: #d9f0f7; background: rgba(2, 8, 12, 150); border: 1px solid rgba(40, 112, 125, 140); border-radius: 7px; padding: 9px; }
        QLabel#PlatformStatus { color: #d8e0e8; background: rgba(0, 0, 0, 135); border: 1px solid rgba(46, 213, 209, 95); border-radius: 8px; padding: 8px; }
        QPushButton { min-height: 36px; border-radius: 8px; font-weight: 700; padding-left: 12px; padding-right: 12px; background: rgba(4, 10, 14, 175); color: #f5fbff; border: 1px solid rgba(56, 93, 107, 165); }
        QPushButton:hover { background: rgba(8, 18, 24, 205); }
        QPushButton#SnapshotButton { background: rgba(4, 10, 14, 180); color: #ffffff; border: 1px solid rgba(37, 234, 215, 215); }
        QPushButton#SnapshotButton:hover { background: rgba(8, 18, 24, 210); border: 1px solid rgba(109, 255, 244, 230); }
        QPushButton#DocSnapshotButton { background: rgba(4, 10, 14, 180); color: #ffffff; border: 1px solid rgba(73, 175, 255, 210); min-width: 120px; }
        QPushButton#DocSnapshotButton:hover { background: rgba(8, 18, 24, 210); border: 1px solid rgba(123, 211, 255, 230); }
        QPushButton#ImplementButton { background: rgba(6, 10, 12, 180); color: #ffffff; border: 1px solid rgba(243, 255, 88, 225); }
        QPushButton#ImplementButton:hover { background: rgba(18, 22, 10, 210); border: 1px solid rgba(250, 255, 133, 235); }
        QPushButton#SecondaryButton { background: rgba(4, 10, 14, 165); color: #ecf9ff; border: 1px solid rgba(71, 167, 224, 180); }
        QPushButton#SecondaryButton:hover { background: rgba(8, 18, 24, 198); border: 1px solid rgba(112, 210, 255, 230); }
        QPushButton#ImageButton { min-width: 145px; min-height: 36px; padding: 2px; background: rgba(4, 10, 14, 175); color: transparent; border: 1px solid rgba(71, 167, 224, 180); }
        QPushButton#ImageButton:hover { background: rgba(8, 18, 24, 198); border: 1px solid rgba(112, 210, 255, 230); }
        QPushButton#ImageButton:disabled { background: rgba(3, 6, 8, 140); border: 1px solid rgba(44, 62, 70, 150); }
        QPushButton#StructureSettingsButton { min-width: 145px; min-height: 36px; padding: 2px; background: rgba(4, 10, 14, 165); color: transparent; border: 1px solid rgba(71, 167, 224, 180); }
        QPushButton#StructureSettingsButton:hover { background: rgba(8, 18, 24, 198); border: 1px solid rgba(112, 210, 255, 230); }
        QPushButton#StructureSettingsButton[active="true"] { background: rgba(0, 112, 145, 205); color: transparent; border: 1px solid rgba(50, 235, 231, 235); }
        QPushButton#StructureSettingsButton[active="true"]:hover { background: rgba(0, 144, 176, 225); border: 1px solid rgba(119, 255, 247, 245); }
        QPushButton#ModuleButton { background: rgba(4, 10, 14, 165); color: #ecf9ff; border: 1px solid rgba(40, 223, 219, 160); text-align: left; }
        QPushButton#ModuleButton:hover { background: rgba(8, 18, 24, 198); border: 1px solid rgba(109, 255, 244, 210); }
        QPushButton:disabled { background: rgba(3, 6, 8, 140); color: #556972; border: 1px solid rgba(44, 62, 70, 150); }

        QFrame#StructureSettingsPanel { background: rgba(3, 8, 12, 105); border: 1px solid rgba(40, 200, 214, 105); border-radius: 10px; }
        QFrame#StructureNavigationView { background: transparent; border: none; }
        QFrame#StructureNavigationContent { background: transparent; border: none; }
        QScrollArea#StructureNavigationScroll { background: transparent; border: none; }
        QPushButton#StructureNavigationButton { min-height: 42px; padding: 8px 12px; border-radius: 8px; background: rgba(5, 14, 20, 190); color: #f5fbff; border: 1px solid rgba(46, 213, 209, 150); font-size: 9.5pt; text-align: left; }
        QPushButton#StructureNavigationButton:hover { background: rgba(8, 28, 38, 220); border: 1px solid rgba(109, 255, 244, 225); }
        QPushButton#StructureNavigationButton[active="true"] { background: rgba(0, 103, 138, 195); color: #ffffff; border: 1px solid rgba(46, 220, 231, 225); }
        QPushButton#StructureNavigationButton[active="true"]:hover { background: rgba(0, 135, 168, 220); border: 1px solid rgba(113, 249, 255, 240); }
        QPushButton#StructureTinyButton { min-height: 26px; padding-left: 10px; padding-right: 10px; border-radius: 7px; background: rgba(5, 14, 20, 180); color: #f5fbff; border: 1px solid rgba(46, 213, 209, 150); font-size: 9pt; }
        QPushButton#StructureTinyButton:hover { background: rgba(8, 22, 31, 210); border: 1px solid rgba(109, 255, 244, 220); }
        QPushButton#StructureTinyButton[active="true"] { background: rgba(0, 103, 138, 195); color: #ffffff; border: 1px solid rgba(46, 220, 231, 225); }
        QPushButton#StructureTinyButton[active="true"]:hover { background: rgba(0, 135, 168, 220); border: 1px solid rgba(113, 249, 255, 240); }
        QFrame#StructureWorkshopView { background: transparent; border: none; }
        QFrame#StructureContentHost { background: transparent; border: none; }
        QLabel#StructurePlaceholder { color: #7fa3ae; background: rgba(0, 0, 0, 92); border: 1px dashed rgba(45, 187, 204, 90); border-radius: 8px; padding: 12px; }
        QFrame#ProductDataForm { background: rgba(0, 0, 0, 80); border: 1px solid rgba(45, 187, 204, 90); border-radius: 9px; }
        QFrame#RoofDataForm { background: rgba(0, 0, 0, 80); border: 1px solid rgba(45, 187, 204, 90); border-radius: 9px; }
        QFrame#DocumentationDataForm { background: rgba(0, 0, 0, 80); border: 1px solid rgba(45, 187, 204, 90); border-radius: 9px; }
        QFrame#GlobalAppFolderStructureForm { background: rgba(0, 0, 0, 80); border: 1px solid rgba(45, 187, 204, 90); border-radius: 9px; }
        QLabel#GlobalAppStructureSubtitle { color: #70dfff; font-size: 9pt; }
        QFrame#GlobalAppStructureTreePanel { background: rgba(4, 10, 14, 125); border: 1px solid rgba(40, 112, 125, 120); border-radius: 8px; }
        QTreeWidget#GlobalAppStructureTree { background: transparent; border: none; outline: none; color: #f2fbff; }
        QTreeWidget#GlobalAppStructureTree::item { height: 24px; padding: 2px 6px; border-radius: 7px; }
        QTreeWidget#GlobalAppStructureTree::item:hover { background: rgba(0, 220, 255, 35); }
        QTreeWidget#GlobalAppStructureTree::item:selected { background: rgba(0, 220, 255, 70); color: #ffffff; }
        QLabel#GlobalAppStructurePathPreview { color: #91a8b8; background: rgba(0, 0, 0, 90); border: 1px solid rgba(0, 216, 255, 80); border-radius: 7px; padding: 6px 8px; }
        QPushButton#GlobalAppStructureButton { min-height: 30px; background: rgba(7, 18, 28, 230); color: #ffffff; border: 1px solid rgba(21, 157, 196, 220); border-radius: 8px; padding-left: 10px; padding-right: 10px; font-weight: 700; }
        QPushButton#GlobalAppStructureButton:hover { background: rgba(0, 120, 160, 120); border: 1px solid #00e4ff; }
        QPushButton#GlobalAppStructureDeleteButton { min-height: 30px; background: rgba(75, 25, 8, 180); color: #ffffff; border: 1px solid #ff8b3d; border-radius: 8px; padding-left: 10px; padding-right: 10px; font-weight: 700; }
        QPushButton#GlobalAppStructureDeleteButton:hover { background: rgba(105, 36, 9, 200); border: 1px solid #ffbd78; }
        QLabel#StructureFormTitle { color: #ffffff; font-size: 13pt; font-weight: 800; }
        QLabel#StructureFormStatus { color: #d8e0e8; background: rgba(0, 0, 0, 115); border: 1px solid rgba(46, 213, 209, 85); border-radius: 7px; padding: 7px; }
        QLabel#StructureFormStatus[error="true"] { color: #ff9aa4; border: 1px solid rgba(255, 75, 95, 130); }
        QScrollArea#RoofDataScroll { background: rgba(0, 0, 0, 70); border: 1px solid rgba(45, 187, 204, 70); border-radius: 8px; }
        QFrame#RoofDataGroup { background: rgba(4, 10, 14, 125); border: 1px solid rgba(40, 112, 125, 120); border-radius: 8px; }
        QLabel#RoofDataGroupTitle { color: #70dfff; font-weight: 800; padding: 3px; }
        
        QComboBox#ProductDataCombo { background: rgba(0, 0, 0, 150); color: #edf7ff; border: 1px solid rgba(46, 213, 209, 100); border-radius: 7px; padding: 6px; min-height: 28px; }
        QComboBox#ProductDataCombo:hover { border: 1px solid rgba(109, 255, 244, 210); }
        QComboBox#ProductDataCombo QAbstractItemView { background: #071017; color: #edf7ff; selection-background-color: rgba(0, 145, 170, 170); border: 1px solid rgba(46, 213, 209, 120); }
        QLineEdit#RoofDataInput { background: rgba(0, 0, 0, 150); color: #edf7ff; border: 1px solid rgba(46, 213, 209, 80); border-radius: 6px; padding: 5px; }
        QLineEdit#RoofDataInput:focus { border: 1px solid rgba(109, 255, 244, 200); }
        QLineEdit#RoofDataInput:disabled { background: rgba(0, 0, 0, 70); color: #677b84; border: 1px solid rgba(44, 62, 70, 120); }
        QLineEdit#RoofDataInput[automatic="true"] { background: rgba(6, 18, 25, 145); color: #89a8b4; border: 1px solid rgba(65, 104, 116, 130); }
        QTextEdit#DocumentationTextInput { background: rgba(0, 0, 0, 150); color: #edf7ff; border: 1px solid rgba(46, 213, 209, 80); border-radius: 6px; padding: 5px; font-family: "Segoe UI", Arial; }
        QTextEdit#DocumentationTextInput:focus { border: 1px solid rgba(109, 255, 244, 200); }
        QTextEdit#DocumentationTextInput:disabled { background: rgba(0, 0, 0, 70); color: #677b84; border: 1px solid rgba(44, 62, 70, 120); }
        QPushButton#StructureSaveButton { min-height: 30px; background: rgba(0, 145, 170, 145); color: #ffffff; border: 1px solid #00e4ff; border-radius: 8px; font-weight: 800; }
        QPushButton#StructureSaveButton:hover { background: rgba(0, 165, 190, 180); }
        QPushButton#SecretSetButton { min-height: 28px; background: rgba(8, 18, 24, 180); color: #ffffff; border: 1px solid rgba(255, 152, 63, 180); border-radius: 7px; font-size: 9pt; padding-left: 9px; padding-right: 9px; }
        QPushButton#SecretSetButton:hover { background: rgba(72, 32, 7, 190); border: 1px solid rgba(255, 190, 84, 230); }
        QPushButton#SecretCopyButton { min-height: 28px; background: rgba(8, 18, 24, 180); color: #ffffff; border: 1px solid rgba(46, 213, 209, 150); border-radius: 7px; font-size: 9pt; padding-left: 9px; padding-right: 9px; }
        QPushButton#SecretCopyButton:hover { background: rgba(0, 120, 160, 120); border: 1px solid rgba(109, 255, 244, 220); }
        QLabel#StatusPanel { background: rgba(0, 0, 0, 145); color: #d8e0e8; border: 1px solid rgba(46, 213, 209, 110); border-radius: 8px; padding: 8px; }
        QTextEdit#LogBox { background: rgba(0, 0, 0, 178); color: #d8e0e8; border: 1px solid rgba(46, 213, 209, 110); border-radius: 8px; font-family: Consolas, monospace; font-size: 9.5pt; }
        QTextEdit#CommitTextBox { background: rgba(0, 0, 0, 168); color: #d8e0e8; border: 1px solid rgba(46, 213, 209, 110); border-radius: 8px; padding: 8px; font-family: Consolas, monospace; font-size: 9.5pt; }
        QTextEdit#CommitTextBox:disabled { background: rgba(0, 0, 0, 120); color: #62757d; border: 1px solid rgba(44, 62, 70, 150); }
        QComboBox#RepositoryProductCombo { background: rgba(0, 0, 0, 150); color: #edf7ff; border: 1px solid rgba(46, 213, 209, 120); border-radius: 8px; padding: 6px 10px; min-height: 30px; }
        QComboBox#RepositoryProductCombo:hover { border: 1px solid rgba(109, 255, 244, 220); }
        QComboBox#RepositoryProductCombo QAbstractItemView { background: #071017; color: #edf7ff; selection-background-color: rgba(0, 145, 170, 170); border: 1px solid rgba(46, 213, 209, 120); }
        QPushButton#RepositoryPushButton { min-height: 34px; background: rgba(0, 130, 160, 170); color: #ffffff; border: 1px solid #00e4ff; border-radius: 8px; padding-left: 14px; padding-right: 14px; font-weight: 800; }
        QPushButton#RepositoryPushButton:hover { background: rgba(0, 165, 190, 205); border: 1px solid rgba(119, 255, 247, 245); }
        QPushButton#RepositoryPushButton:disabled { background: rgba(3, 6, 8, 140); color: #556972; border: 1px solid rgba(44, 62, 70, 150); }
        QFrame#RepositoryImageDropBox { background: rgba(0, 0, 0, 115); border: 2px dashed rgba(46, 213, 209, 135); border-radius: 10px; }
        QFrame#RepositoryImageDropBox:hover { background: rgba(0, 115, 145, 60); border: 2px dashed rgba(109, 255, 244, 220); }
        QFrame#RepositoryImageDropBox:disabled { background: rgba(0, 0, 0, 70); border: 2px dashed rgba(41, 71, 81, 140); }
        QLabel#RepositoryImageCrosshair { color: #72c7ff; font-size: 28pt; font-weight: 900; background: transparent; }
        QScrollArea { background: rgba(0, 0, 0, 72); border: 1px solid rgba(45, 187, 204, 90); border-radius: 8px; }
    """
