from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")



def apply_manufacturer_wizard_style(widget) -> None:
    widget.setStyleSheet("""
        QDialog { background: #090d12; color: #eef8ff; }
        QLabel#ManufacturerWizardTitle { color: #ffffff; font-size: 14pt; font-weight: 800; }
        QLabel#ManufacturerWizardHint { color: #8fb8c5; font-size: 10pt; }
        QLabel#ManufacturerWizardLabel { color: #d8e8ef; font-weight: 700; }
        QLabel#ManufacturerWizardSectionTitle { color: #66deef; font-weight: 800; font-size: 10.5pt; padding-bottom: 3px; }
        QLabel#ManufacturerWizardFixedValue { min-height: 30px; background: rgba(5, 20, 28, 220); color: #66deef; border: 1px solid rgba(40, 173, 198, 110); border-radius: 7px; padding: 4px 8px; font-weight: 700; }
        QLabel#ManufacturerWizardSummary { background: rgba(3, 12, 17, 220); border: 1px solid rgba(40, 173, 198, 150); border-radius: 9px; padding: 14px; color: #eafaff; }
        QLineEdit#ManufacturerWizardInput, QSpinBox#ManufacturerWizardSpinBox { min-height: 30px; background: rgba(2, 10, 15, 220); color: #eef8ff; border: 1px solid rgba(40, 173, 198, 145); border-radius: 7px; padding: 4px 8px; }
        QLineEdit#ManufacturerWizardInput:focus, QSpinBox#ManufacturerWizardSpinBox:focus { border-color: #00e4ff; }
        QRadioButton#ManufacturerWizardRadio { min-height: 38px; padding: 0 12px; border: 1px solid rgba(40, 173, 198, 145); border-radius: 8px; background: rgba(4, 14, 20, 210); font-weight: 700; }
        QRadioButton#ManufacturerWizardRadio:hover { border-color: #00d8ff; background: rgba(0, 115, 140, 55); }
        QRadioButton#ManufacturerWizardRadio::indicator { width: 18px; height: 18px; margin-right: 9px; }
        QFrame#ManufacturerWizardCard { background: rgba(3, 12, 17, 185); border: 1px solid rgba(40, 173, 198, 110); border-radius: 9px; }
        QPushButton#ManufacturerWizardCancelButton, QPushButton#ManufacturerWizardBackButton, QPushButton#ManufacturerWizardNextButton, QPushButton#ManufacturerWizardFinishButton { min-height: 30px; border-radius: 7px; padding: 4px 12px; font-weight: 700; }
        QPushButton#ManufacturerWizardCancelButton, QPushButton#ManufacturerWizardBackButton { color: #ffffff; background: rgba(15, 28, 36, 220); border: 1px solid #387486; }
        QPushButton#ManufacturerWizardNextButton, QPushButton#ManufacturerWizardFinishButton { color: #ffffff; background: rgba(0, 137, 161, 190); border: 1px solid #00e4ff; }
        QPushButton#ManufacturerWizardCancelButton:hover, QPushButton#ManufacturerWizardBackButton:hover { border-color: #00d8ff; }
        QPushButton#ManufacturerWizardNextButton:hover, QPushButton#ManufacturerWizardFinishButton:hover { background: rgba(0, 179, 205, 215); }
    """)
