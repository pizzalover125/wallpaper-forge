import sys, json
from PyQt6.QtWidgets import ( # type: ignore
    QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QMainWindow,
    QCheckBox, QComboBox, QLineEdit, QSlider, QHBoxLayout, QColorDialog,
    QGridLayout, QGroupBox
)
from PyQt6.QtGui import QPixmap, QImage, QColor # type: ignore
from PyQt6.QtCore import Qt # type: ignore
from script import WallpaperForge, load_config, CONFIG_PATH

class WallpaperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wallpaper Forge")
        self.resize(700, 500)
        self.config = load_config()
        self.initUI()

    def saveConfig(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    def initUI(self):
        main_layout = QHBoxLayout()
        
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.preview = QLabel("Preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(400, 225)
        self.preview.setMaximumSize(400, 225)
        self.preview.setStyleSheet("border: 1px solid gray;")
        
        button_layout = QHBoxLayout()
        self.genBtn = QPushButton("Generate")
        self.applyBtn = QPushButton("Apply")
        button_layout.addWidget(self.genBtn)
        button_layout.addWidget(self.applyBtn)
        
        self.genBtn.clicked.connect(self.generate)
        self.applyBtn.clicked.connect(self.apply)
        
        left_layout.addWidget(self.preview)
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        content_group = QGroupBox("Content")
        content_layout = QGridLayout()
        
        self.msgToggle = QCheckBox("Show Message")
        self.msgToggle.setChecked(self.config["show_message"])
        self.msgToggle.stateChanged.connect(lambda s: self.updateConfig("show_message", bool(s)))
        
        self.messageTypeCombo = QComboBox()
        self.messageTypeCombo.addItems(["Greeting", "Quote"])
        self.messageTypeCombo.setCurrentText(self.config.get("message_type", "Greeting"))
        self.messageTypeCombo.currentTextChanged.connect(self.updateMessageType)
        
        self.timeCombo = QComboBox()
        self.timeCombo.addItems(["None", "Time", "Date", "Both Time and Date"])
        self.timeCombo.setCurrentText(self.config.get("time_display", "Time"))
        self.timeCombo.currentTextChanged.connect(self.updateTimeDisplay)
        
        self.weatherToggle = QCheckBox("Show Weather")
        self.weatherToggle.setChecked(self.config.get("show_weather", True))
        self.weatherToggle.stateChanged.connect(lambda s: self.updateConfig("show_weather", bool(s)))
        
        content_layout.addWidget(self.msgToggle, 0, 0)
        content_layout.addWidget(self.messageTypeCombo, 0, 1)
        content_layout.addWidget(QLabel("Time:"), 1, 0)
        content_layout.addWidget(self.timeCombo, 1, 1)
        content_layout.addWidget(self.weatherToggle, 2, 0, 1, 2)
        content_group.setLayout(content_layout)
        
        self.weatherLocationInput = QLineEdit()
        self.weatherLocationInput.setPlaceholderText("Weather location (e.g., Phoenix,AZ)")
        self.weatherLocationInput.setText(self.config.get("weather_location", "Phoenix,AZ"))
        self.weatherLocationInput.textChanged.connect(self.updateWeatherLocation)
        
        overlay_group = QGroupBox("Overlay")
        overlay_layout = QVBoxLayout()
        
        self.overlayToggle = QCheckBox("Enable Overlay")
        self.overlayToggle.setChecked(self.config.get("overlay_enabled", True))
        self.overlayToggle.stateChanged.connect(self.updateOverlayEnabled)
        
        self.colorBtn = QPushButton("Color")
        self.colorBtn.setMaximumWidth(80)
        self.colorBtn.clicked.connect(self.chooseColor)
        self.updateColorButton()
        
        color_opacity_layout = QHBoxLayout()
        color_opacity_layout.addWidget(self.colorBtn)
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        self.opacitySlider = QSlider(Qt.Orientation.Horizontal)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(255)
        self.opacitySlider.setValue(self.config.get("overlay_opacity", 80))
        self.opacitySlider.setMinimumWidth(100)
        self.opacitySlider.valueChanged.connect(self.updateOpacity)
        
        self.opacityLabel = QLabel(str(self.config.get("overlay_opacity", 80)))
        self.opacityLabel.setMinimumWidth(30)
        
        opacity_layout.addWidget(self.opacitySlider)
        opacity_layout.addWidget(self.opacityLabel)
        
        overlay_layout.addWidget(self.overlayToggle)
        overlay_layout.addLayout(color_opacity_layout)
        overlay_layout.addLayout(opacity_layout)
        overlay_group.setLayout(overlay_layout)
        
        source_group = QGroupBox("Image Source")
        source_layout = QVBoxLayout()
        
        self.sourceCombo = QComboBox()
        self.sourceCombo.addItems(["Random image from Picsum", "Custom URL"])
        current_source = self.config["image_source"]
        self.sourceCombo.setCurrentText(current_source)
        self.sourceCombo.currentTextChanged.connect(self.changeSource)
        
        self.urlInput = QLineEdit()
        self.urlInput.setPlaceholderText("Enter image URL")
        self.urlInput.setText(self.config.get("custom_url", ""))
        self.urlInput.textChanged.connect(self.updateUrl)
        self.urlInput.setVisible(self.sourceCombo.currentText() == "Custom URL")
        
        source_layout.addWidget(self.sourceCombo)
        source_layout.addWidget(self.urlInput)
        source_group.setLayout(source_layout)

        self.fontInput = QLineEdit()
        self.fontInput.setPlaceholderText("Custom font URL (optional)")
        self.fontInput.setText(self.config.get("google_font_url", ""))
        self.fontInput.textChanged.connect(self.updateFontUrl)
        
        font_group = QGroupBox("Font Sizes")
        font_layout = QGridLayout()
        
        font_layout.addWidget(QLabel("Message:"), 0, 0)
        self.messageFontSlider = QSlider(Qt.Orientation.Horizontal)
        self.messageFontSlider.setMinimum(20)
        self.messageFontSlider.setMaximum(160)
        self.messageFontSlider.setValue(self.config.get("font_size_message", 80))
        self.messageFontSlider.valueChanged.connect(self.updateMessageFontSize)
        self.messageFontLabel = QLabel(str(self.config.get("font_size_message", 80)))
        self.messageFontLabel.setMinimumWidth(30)
        font_layout.addWidget(self.messageFontSlider, 0, 1)
        font_layout.addWidget(self.messageFontLabel, 0, 2)
        
        font_layout.addWidget(QLabel("Weather:"), 1, 0)
        self.weatherFontSlider = QSlider(Qt.Orientation.Horizontal)
        self.weatherFontSlider.setMinimum(20)
        self.weatherFontSlider.setMaximum(120)
        self.weatherFontSlider.setValue(self.config.get("font_size_weather", 60))
        self.weatherFontSlider.valueChanged.connect(self.updateWeatherFontSize)
        self.weatherFontLabel = QLabel(str(self.config.get("font_size_weather", 60)))
        self.weatherFontLabel.setMinimumWidth(30)
        font_layout.addWidget(self.weatherFontSlider, 1, 1)
        font_layout.addWidget(self.weatherFontLabel, 1, 2)
        
        font_layout.addWidget(QLabel("Time:"), 2, 0)
        self.timeFontSlider = QSlider(Qt.Orientation.Horizontal)
        self.timeFontSlider.setMinimum(20)
        self.timeFontSlider.setMaximum(160)
        self.timeFontSlider.setValue(self.config.get("font_size_time", 80))
        self.timeFontSlider.valueChanged.connect(self.updateTimeFontSize)
        self.timeFontLabel = QLabel(str(self.config.get("font_size_time", 80)))
        self.timeFontLabel.setMinimumWidth(30)
        font_layout.addWidget(self.timeFontSlider, 2, 1)
        font_layout.addWidget(self.timeFontLabel, 2, 2)
        
        font_group.setLayout(font_layout)
        
        right_layout.addWidget(content_group)
        right_layout.addWidget(self.weatherLocationInput)
        right_layout.addWidget(overlay_group)
        right_layout.addWidget(source_group)
        right_layout.addWidget(QLabel("Font:"))
        right_layout.addWidget(self.fontInput)
        right_layout.addWidget(font_group)
        right_layout.addStretch()
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.forge = WallpaperForge(self.config)
        self.imagePath = None
        self.generate()

    def updateConfig(self, key, value):
        self.config[key] = value
        self.saveConfig()

    def updateWeatherLocation(self, location):
        self.config["weather_location"] = location
        self.saveConfig()

    def changeSource(self, value):
        self.config["image_source"] = value
        self.saveConfig()
        self.urlInput.setVisible(value == "Custom URL")

    def updateUrl(self, url):
        self.config["custom_url"] = url
        self.saveConfig()

    def updateFontUrl(self, url):
        self.config["google_font_url"] = url
        self.saveConfig()

    def updateMessageType(self, value):
        self.config["message_type"] = value
        self.saveConfig()

    def updateTimeDisplay(self, value):
        self.config["time_display"] = value
        self.saveConfig()

    def chooseColor(self):
        current_color = QColor(self.config.get("overlay_color", "#000000"))
        
        color = QColorDialog.getColor(current_color, self, "Choose Overlay Color")
        
        if color.isValid():
            hex_color = color.name()
            self.config["overlay_color"] = hex_color
            self.saveConfig()
            self.updateColorButton()

    def updateColorButton(self):
        color = self.config.get("overlay_color", "#000000")
        self.colorBtn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; }}")
        self.colorBtn.setText("Color")

    def updateOverlayEnabled(self, state):
        self.config["overlay_enabled"] = bool(state)
        self.saveConfig()

    def updateOpacity(self, value):
        self.config["overlay_opacity"] = value
        self.opacityLabel.setText(str(value))
        self.saveConfig()

    def updateMessageFontSize(self, value):
        self.config["font_size_message"] = value
        self.messageFontLabel.setText(str(value))
        self.saveConfig()

    def updateWeatherFontSize(self, value):
        self.config["font_size_weather"] = value
        self.weatherFontLabel.setText(str(value))
        self.saveConfig()

    def updateTimeFontSize(self, value):
        self.config["font_size_time"] = value
        self.timeFontLabel.setText(str(value))
        self.saveConfig()

    def generate(self):
        self.forge = WallpaperForge(self.config)
        self.imagePath = self.forge.generateWallpaper()
        self.showPreview(self.imagePath)

    def apply(self):
        if self.imagePath:
            self.forge.setWallpaper()

    def showPreview(self, path):
        img = QImage(path)
        pixmap = QPixmap.fromImage(img.scaled(400, 225, Qt.AspectRatioMode.KeepAspectRatio))
        self.preview.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WallpaperApp()
    window.show()
    sys.exit(app.exec())