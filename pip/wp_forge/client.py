import sys, json, os
from PyQt6.QtWidgets import ( # type: ignore
    QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QMainWindow,
    QCheckBox, QComboBox, QLineEdit, QSlider, QHBoxLayout, QColorDialog,
    QGridLayout, QGroupBox, QScrollArea, QTabWidget, QMessageBox, QTextEdit,
    QSpinBox
)
from PyQt6.QtGui import QPixmap, QImage, QColor, QIcon # type: ignore
from PyQt6.QtCore import Qt # type: ignore
from wp_forge.script import WallpaperForge, load_config, CONFIG_PATH

class GalleryWidget(QWidget):
    # initalizes the whole application
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        with open(os.path.join(os.path.dirname(__file__), "backgrounds.json"), "r") as f:
            self.predefined_wallpapers = json.load(f) 
        self.initUI()
        self.loadGallery()

    # initializes the UI components 
    def initUI(self):
        layout = QVBoxLayout()

        title_label = QLabel("Select a Background Image")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        
        self.scroll_area.setWidget(self.gallery_widget)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)

    # loads the gallery with predefined wallpapers
    def loadGallery(self):
        for i in reversed(range(self.gallery_layout.count())):
            child = self.gallery_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.predefined_wallpapers:
            no_files_label = QLabel("No wallpapers available.")
            no_files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_files_label.setStyleSheet("color: gray; font-size: 14px; padding: 20px;")
            self.gallery_layout.addWidget(no_files_label, 0, 0)
            return
        
        row, col = 0, 0
        for wallpaper in self.predefined_wallpapers: 
            self.addGalleryItem(wallpaper, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    # helper function to add a given wallpaper to the gallery
    def addGalleryItem(self, wallpaper_data, row, col):
        item_widget = QWidget()
        item_widget.setMaximumSize(260, 200)
        item_widget.setStyleSheet("""
            background: #23272e;
            border: 1px solid #2c313a;
            border-radius: 6px;
            margin: 6px;
        """)
        
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 10, 10, 10)
        item_layout.setSpacing(8)

        thumbnail = QLabel()
        thumbnail.setMinimumSize(220, 120)
        thumbnail.setMaximumSize(220, 120)
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail.setStyleSheet("""
            border: 1px solid #2c313a;
            background: #181a20;
            border-radius: 4px;
            margin: 2px;
        """)

        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            response = requests.get(wallpaper_data["url"], timeout=5)
            if response.status_code == 200:
                pil_image = Image.open(BytesIO(response.content))
                pil_image = pil_image.resize((220, 120), Image.Resampling.LANCZOS)
                pil_image = pil_image.convert('RGB')
                qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                thumbnail.setPixmap(pixmap)
            else:
                thumbnail.setText("Preview\nUnavailable")
        except Exception:
            thumbnail.setText(f"{wallpaper_data['name']}\nPreview")
            thumbnail.setStyleSheet(thumbnail.styleSheet() + "color: #888; font-size: 12px;")
        
        item_layout.addWidget(thumbnail)
        
        name_label = QLabel(wallpaper_data["name"])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: 500; 
            color: #e6e6e6;
            border: none;
            margin: 2px;
            letter-spacing: 0.5px;asdasd
        """)
        item_layout.addWidget(name_label)

        desc_label = QLabel(wallpaper_data["description"])
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            font-size: 11px; 
            color: #b0b3b8; 
            border: none; 
            margin: 2px;
        """)
        desc_label.setWordWrap(True)
        item_layout.addWidget(desc_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        select_btn = QPushButton("Select")
        select_btn.setMinimumHeight(32)
        select_btn.setMaximumHeight(36)
        select_btn.setMinimumWidth(80)
        select_btn.setStyleSheet("""
            QPushButton {
            background: #3a3f4b;
            color: #fff;
            font-weight: 500;
            border-radius: 4px;
            border: none;
            padding: 6px 18px;
            font-size: 13px;
            }
            QPushButton:hover {
            background: #50576a;
            }
        """) 
        select_btn.clicked.connect(lambda checked, data=wallpaper_data: self.selectWallpaper(data))
        
        preview_btn = QPushButton("Preview")
        preview_btn.setMinimumHeight(32)
        preview_btn.setMaximumHeight(36)
        preview_btn.setMinimumWidth(80)
        preview_btn.setStyleSheet("""
            QPushButton {
            background: #23272e;
            color: #e6e6e6;
            font-weight: 500;
            border-radius: 4px;
            border: 1px solid #444950;
            padding: 6px 18px;
            font-size: 13px;
            }
            QPushButton:hover {
            background: #2c313a;
            border: 1px solid #888;
            }
        """)
        preview_btn.clicked.connect(lambda checked, data=wallpaper_data: self.previewWallpaper(data))
        button_layout.addWidget(select_btn)
        button_layout.addWidget(preview_btn)
        
        item_layout.addLayout(button_layout)
        
        self.gallery_layout.addWidget(item_widget, row, col)

    # selects a wallpaper and prints a message
    def selectWallpaper(self, wallpaper_data):
        self.parent.config["image_source"] = "Custom URL"
        self.parent.config["custom_url"] = wallpaper_data["url"]
        self.parent.saveConfig()
        
        self.parent.sourceCombo.setCurrentText("Custom URL")
        self.parent.urlInput.setText(wallpaper_data["url"])
        self.parent.urlInput.setVisible(True)
        
        self.parent.tab_widget.setCurrentIndex(0)
        QMessageBox.information(
            self, 
            "Background Selected", 
            f"'{wallpaper_data['name']}' has been selected as your background image.\n\nClick 'Generate' to create your wallpaper with this background."
        )

    # previews the selected wallpaper in the main tab
    def previewWallpaper(self, wallpaper_data):
        original_source = self.parent.config["image_source"]
        original_url = self.parent.config.get("custom_url", "")
        
        self.parent.config["image_source"] = "Custom URL"
        self.parent.config["custom_url"] = wallpaper_data["url"]

        try: 
            forge = WallpaperForge(self.parent.config)
            preview_path = forge.generateWallpaper()
            self.parent.showPreview(preview_path)
            self.parent.imagePath = preview_path
            
            self.parent.tab_widget.setCurrentIndex(0)
            
            QMessageBox.information(
                self, 
                "Preview Generated", 
                f"Preview of '{wallpaper_data['name']}' generated with your current settings.\n\nIf you like it, click 'Apply' to set it as your wallpaper."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to generate preview: {str(e)}")
        finally:
            self.parent.config["image_source"] = original_source
            self.parent.config["custom_url"] = original_url 

class WallpaperApp(QMainWindow):
    # initializes the main application window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wallpaper Forge")
        self.resize(1100, 700)
        
        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))
        
        self.config = load_config()
        self.initUI()
    
    # saves the current configuration to a JSON file
    def saveConfig(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    # initializes the UI components
    def initUI(self):
        self.tab_widget = QTabWidget()
        
        main_tab = QWidget()
        self.setupMainTab(main_tab)
        self.tab_widget.addTab(main_tab, "Generator")
        
        filters_tab = QWidget()
        self.setupFiltersTab(filters_tab)
        self.tab_widget.addTab(filters_tab, "Image Filters")
        
        self.gallery_tab = GalleryWidget(self)
        self.tab_widget.addTab(self.gallery_tab, "Gallery")
        
        self.setCentralWidget(self.tab_widget)
        
        self.forge = WallpaperForge(self.config)
        self.imagePath = None
        self.generate()

    # sets up the main tab UI components
    def setupMainTab(self, main_tab):
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
        self.messageTypeCombo.addItems(["Greeting", "Quote", "Custom"])
        self.messageTypeCombo.setCurrentText(self.config.get("message_type", "Greeting"))
        self.messageTypeCombo.currentTextChanged.connect(self.updateMessageType)
        
        self.customMessageInput = QTextEdit()
        self.customMessageInput.setMaximumHeight(80)
        self.customMessageInput.setPlaceholderText("Enter your custom message here...")
        self.customMessageInput.setText(self.config.get("custom_message", ""))
        self.customMessageInput.textChanged.connect(self.updateCustomMessage)
        self.customMessageInput.setVisible(self.messageTypeCombo.currentText() == "Custom")
        
        self.timeCombo = QComboBox()
        self.timeCombo.addItems(["None", "Time", "Date", "Both Time and Date"])
        self.timeCombo.setCurrentText(self.config.get("time_display", "Time"))
        self.timeCombo.currentTextChanged.connect(self.updateTimeDisplay)
        
        self.weatherToggle = QCheckBox("Show Weather")
        self.weatherToggle.setChecked(self.config.get("show_weather", True))
        self.weatherToggle.stateChanged.connect(lambda s: self.updateConfig("show_weather", bool(s)))
        
        content_layout.addWidget(self.msgToggle, 0, 0)
        content_layout.addWidget(self.messageTypeCombo, 0, 1)
        content_layout.addWidget(self.customMessageInput, 1, 0, 1, 2)
        content_layout.addWidget(QLabel("Time:"), 2, 0)
        content_layout.addWidget(self.timeCombo, 2, 1)
        content_layout.addWidget(self.weatherToggle, 3, 0, 1, 2)
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
        opacity_label = QLabel("Opacity:")
        opacity_label.setToolTip("Setting Opacity to 255 will result in a solid color")
        opacity_layout.addWidget(opacity_label)
        
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
        
        main_tab.setLayout(main_layout)

    # sets up the filters tab UI components
    def setupFiltersTab(self, filters_tab):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        master_group = QGroupBox("Filter Controls")
        master_layout = QHBoxLayout()
        
        self.filtersToggle = QCheckBox("Enable Image Filters")
        self.filtersToggle.setChecked(self.config.get("filters_enabled", True))
        self.filtersToggle.stateChanged.connect(lambda s: self.updateConfig("filters_enabled", bool(s)))
        master_layout.addWidget(self.filtersToggle)
        
        reset_btn = QPushButton("Reset All Filters")
        reset_btn.clicked.connect(self.resetAllFilters)
        master_layout.addWidget(reset_btn)
        master_layout.addStretch()
        
        master_group.setLayout(master_layout)
        main_layout.addWidget(master_group)

        enhance_group = QGroupBox("Basic Enhancements")
        enhance_layout = QGridLayout()
        
        enhance_layout.addWidget(QLabel("Brightness:"), 0, 0)
        self.brightnessSlider = QSlider(Qt.Orientation.Horizontal)
        self.brightnessSlider.setMinimum(0)
        self.brightnessSlider.setMaximum(200)
        self.brightnessSlider.setValue(self.config.get("brightness", 100))
        self.brightnessSlider.valueChanged.connect(self.updateBrightness)
        self.brightnessLabel = QLabel(str(self.config.get("brightness", 100)))
        enhance_layout.addWidget(self.brightnessSlider, 0, 1)
        enhance_layout.addWidget(self.brightnessLabel, 0, 2)
        
        enhance_layout.addWidget(QLabel("Contrast:"), 1, 0)
        self.contrastSlider = QSlider(Qt.Orientation.Horizontal)
        self.contrastSlider.setMinimum(0)
        self.contrastSlider.setMaximum(200)
        self.contrastSlider.setValue(self.config.get("contrast", 100))
        self.contrastSlider.valueChanged.connect(self.updateContrast)
        self.contrastLabel = QLabel(str(self.config.get("contrast", 100)))
        enhance_layout.addWidget(self.contrastSlider, 1, 1)
        enhance_layout.addWidget(self.contrastLabel, 1, 2)

        enhance_layout.addWidget(QLabel("Saturation:"), 2, 0)
        self.saturationSlider = QSlider(Qt.Orientation.Horizontal)
        self.saturationSlider.setMinimum(0)
        self.saturationSlider.setMaximum(200)
        self.saturationSlider.setValue(self.config.get("saturation", 100))
        self.saturationSlider.valueChanged.connect(self.updateSaturation)
        self.saturationLabel = QLabel(str(self.config.get("saturation", 100)))
        enhance_layout.addWidget(self.saturationSlider, 2, 1)
        enhance_layout.addWidget(self.saturationLabel, 2, 2)

        enhance_layout.addWidget(QLabel("Sharpness:"), 3, 0)
        self.sharpnessSlider = QSlider(Qt.Orientation.Horizontal)
        self.sharpnessSlider.setMinimum(0)
        self.sharpnessSlider.setMaximum(200)
        self.sharpnessSlider.setValue(self.config.get("sharpness", 100))
        self.sharpnessSlider.valueChanged.connect(self.updateSharpness)
        self.sharpnessLabel = QLabel(str(self.config.get("sharpness", 100)))
        enhance_layout.addWidget(self.sharpnessSlider, 3, 1)
        enhance_layout.addWidget(self.sharpnessLabel, 3, 2)
        
        enhance_group.setLayout(enhance_layout)
        main_layout.addWidget(enhance_group)
        
        effects_group = QGroupBox("Effect Filters")
        effects_layout = QGridLayout()
        
        self.blurToggle = QCheckBox("Blur")
        self.blurToggle.setChecked(self.config.get("blur_enabled", False))
        self.blurToggle.stateChanged.connect(lambda s: self.updateConfig("blur_enabled", bool(s)))
        effects_layout.addWidget(self.blurToggle, 0, 0)
        
        self.blurIntensitySlider = QSlider(Qt.Orientation.Horizontal)
        self.blurIntensitySlider.setMinimum(1)
        self.blurIntensitySlider.setMaximum(10)
        self.blurIntensitySlider.setValue(self.config.get("blur_intensity", 2))
        self.blurIntensitySlider.valueChanged.connect(self.updateBlurIntensity)
        self.blurIntensityLabel = QLabel(str(self.config.get("blur_intensity", 2)))
        effects_layout.addWidget(self.blurIntensitySlider, 0, 1)
        effects_layout.addWidget(self.blurIntensityLabel, 0, 2)
        
        self.vintageToggle = QCheckBox("Vintage")
        self.vintageToggle.setChecked(self.config.get("vintage_enabled", False))
        self.vintageToggle.stateChanged.connect(lambda s: self.updateConfig("vintage_enabled", bool(s)))
        effects_layout.addWidget(self.vintageToggle, 1, 0)
        
        self.vintageIntensitySlider = QSlider(Qt.Orientation.Horizontal)
        self.vintageIntensitySlider.setMinimum(0)
        self.vintageIntensitySlider.setMaximum(100)
        self.vintageIntensitySlider.setValue(self.config.get("vintage_intensity", 50))
        self.vintageIntensitySlider.valueChanged.connect(self.updateVintageIntensity)
        self.vintageIntensityLabel = QLabel(str(self.config.get("vintage_intensity", 50)))
        effects_layout.addWidget(self.vintageIntensitySlider, 1, 1)
        effects_layout.addWidget(self.vintageIntensityLabel, 1, 2)
        
        self.vignetteToggle = QCheckBox("Vignette")
        self.vignetteToggle.setChecked(self.config.get("vignette_enabled", False))
        self.vignetteToggle.stateChanged.connect(lambda s: self.updateConfig("vignette_enabled", bool(s)))
        effects_layout.addWidget(self.vignetteToggle, 2, 0)
        
        self.vignetteIntensitySlider = QSlider(Qt.Orientation.Horizontal)
        self.vignetteIntensitySlider.setMinimum(0)
        self.vignetteIntensitySlider.setMaximum(100)
        self.vignetteIntensitySlider.setValue(self.config.get("vignette_intensity", 50))
        self.vignetteIntensitySlider.valueChanged.connect(self.updateVignetteIntensity)
        self.vignetteIntensityLabel = QLabel(str(self.config.get("vignette_intensity", 50)))
        effects_layout.addWidget(self.vignetteIntensitySlider, 2, 1)
        effects_layout.addWidget(self.vignetteIntensityLabel, 2, 2)
        
        self.noiseToggle = QCheckBox("Film Grain")
        self.noiseToggle.setChecked(self.config.get("noise_enabled", False))
        self.noiseToggle.stateChanged.connect(lambda s: self.updateConfig("noise_enabled", bool(s)))
        effects_layout.addWidget(self.noiseToggle, 3, 0)
        
        self.noiseIntensitySlider = QSlider(Qt.Orientation.Horizontal)
        self.noiseIntensitySlider.setMinimum(5)
        self.noiseIntensitySlider.setMaximum(50)
        self.noiseIntensitySlider.setValue(self.config.get("noise_intensity", 25))
        self.noiseIntensitySlider.valueChanged.connect(self.updateNoiseIntensity)
        self.noiseIntensityLabel = QLabel(str(self.config.get("noise_intensity", 25)))
        effects_layout.addWidget(self.noiseIntensitySlider, 3, 1)
        effects_layout.addWidget(self.noiseIntensityLabel, 3, 2)
        
        effects_group.setLayout(effects_layout)
        main_layout.addWidget(effects_group)
        
        color_group = QGroupBox("Color Effects")
        color_layout = QGridLayout()
        
        self.sepiaToggle = QCheckBox("Sepia")
        self.sepiaToggle.setChecked(self.config.get("sepia_enabled", False))
        self.sepiaToggle.stateChanged.connect(lambda s: self.updateConfig("sepia_enabled", bool(s)))
        color_layout.addWidget(self.sepiaToggle, 0, 0)
        
        self.grayscaleToggle = QCheckBox("Grayscale")
        self.grayscaleToggle.setChecked(self.config.get("grayscale_enabled", False))
        self.grayscaleToggle.stateChanged.connect(lambda s: self.updateConfig("grayscale_enabled", bool(s)))
        color_layout.addWidget(self.grayscaleToggle, 0, 1)
        
        self.invertToggle = QCheckBox("Invert Colors")
        self.invertToggle.setChecked(self.config.get("invert_enabled", False))
        self.invertToggle.stateChanged.connect(lambda s: self.updateConfig("invert_enabled", bool(s)))
        color_layout.addWidget(self.invertToggle, 1, 0)

        self.posterizeToggle = QCheckBox("Posterize")
        self.posterizeToggle.setChecked(self.config.get("posterize_enabled", False))
        self.posterizeToggle.stateChanged.connect(lambda s: self.updateConfig("posterize_enabled", bool(s)))
        color_layout.addWidget(self.posterizeToggle, 1, 1)
        
        color_layout.addWidget(QLabel("Bits:"), 2, 0)
        self.posterizeBitsSpinner = QSpinBox()
        self.posterizeBitsSpinner.setMinimum(1)
        self.posterizeBitsSpinner.setMaximum(8)
        self.posterizeBitsSpinner.setValue(self.config.get("posterize_bits", 4))
        self.posterizeBitsSpinner.valueChanged.connect(self.updatePosterizeBits)
        color_layout.addWidget(self.posterizeBitsSpinner, 2, 1)
        
        color_group.setLayout(color_layout)
        main_layout.addWidget(color_group)
        
        art_group = QGroupBox("Artistic Effects")
        art_layout = QGridLayout()
        
        self.edgeEnhanceToggle = QCheckBox("Edge Enhance")
        self.edgeEnhanceToggle.setChecked(self.config.get("edge_enhance_enabled", False))
        self.edgeEnhanceToggle.stateChanged.connect(lambda s: self.updateConfig("edge_enhance_enabled", bool(s)))
        art_layout.addWidget(self.edgeEnhanceToggle, 0, 0)
        
        self.embossToggle = QCheckBox("Emboss")
        self.embossToggle.setChecked(self.config.get("emboss_enabled", False))
        self.embossToggle.stateChanged.connect(lambda s: self.updateConfig("emboss_enabled", bool(s)))
        art_layout.addWidget(self.embossToggle, 0, 1)
        
        art_group.setLayout(art_layout)
        main_layout.addWidget(art_group)
        
        main_layout.addStretch()
        main_widget.setLayout(main_layout)
        
        scroll_area.setWidget(main_widget)
        filters_layout = QVBoxLayout()
        filters_layout.addWidget(scroll_area)
        filters_tab.setLayout(filters_layout)

    # resets all filters to their default values
    def resetAllFilters(self):
        filter_defaults = {
            "brightness": 100,
            "contrast": 100,
            "saturation": 100,
            "sharpness": 100,
            "blur_enabled": False,
            "blur_intensity": 2,
            "vintage_enabled": False,
            "vintage_intensity": 50,
            "vignette_enabled": False,
            "vignette_intensity": 50,
            "sepia_enabled": False,
            "grayscale_enabled": False,
            "invert_enabled": False,
            "posterize_enabled": False,
            "posterize_bits": 4,
            "edge_enhance_enabled": False,
            "emboss_enabled": False,
            "noise_enabled": False,
            "noise_intensity": 25
        }
        
        for key, value in filter_defaults.items():
            self.config[key] = value
        self.saveConfig()

        self.brightnessSlider.setValue(100)
        self.contrastSlider.setValue(100)
        self.saturationSlider.setValue(100)
        self.sharpnessSlider.setValue(100)
        self.blurToggle.setChecked(False)
        self.blurIntensitySlider.setValue(2)
        self.vintageToggle.setChecked(False)
        self.vintageIntensitySlider.setValue(50)
        self.vignetteToggle.setChecked(False)
        self.vignetteIntensitySlider.setValue(50)
        self.sepiaToggle.setChecked(False)
        self.grayscaleToggle.setChecked(False)
        self.invertToggle.setChecked(False)
        self.posterizeToggle.setChecked(False)
        self.posterizeBitsSpinner.setValue(4)
        self.edgeEnhanceToggle.setChecked(False)
        self.embossToggle.setChecked(False)
        self.noiseToggle.setChecked(False)
        self.noiseIntensitySlider.setValue(25)

    # bunch of update methods to handle changes in the configuration
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
        self.customMessageInput.setVisible(value == "Custom")

    def updateCustomMessage(self):
        self.config["custom_message"] = self.customMessageInput.toPlainText()
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

    def updateBrightness(self, value):
        self.config["brightness"] = value
        self.brightnessLabel.setText(str(value))
        self.saveConfig()

    def updateContrast(self, value):
        self.config["contrast"] = value
        self.contrastLabel.setText(str(value))
        self.saveConfig()

    def updateSaturation(self, value):
        self.config["saturation"] = value
        self.saturationLabel.setText(str(value))
        self.saveConfig()

    def updateSharpness(self, value):
        self.config["sharpness"] = value
        self.sharpnessLabel.setText(str(value))
        self.saveConfig()

    def updateBlurIntensity(self, value):
        self.config["blur_intensity"] = value
        self.blurIntensityLabel.setText(str(value))
        self.saveConfig()

    def updateVintageIntensity(self, value):
        self.config["vintage_intensity"] = value
        self.vintageIntensityLabel.setText(str(value))
        self.saveConfig()

    def updateVignetteIntensity(self, value):
        self.config["vignette_intensity"] = value
        self.vignetteIntensityLabel.setText(str(value))
        self.saveConfig()

    def updateNoiseIntensity(self, value):
        self.config["noise_intensity"] = value
        self.noiseIntensityLabel.setText(str(value))
        self.saveConfig()

    def updatePosterizeBits(self, value):
        self.config["posterize_bits"] = value
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

def main():
    app = QApplication(sys.argv)
    
    if os.path.exists("icon.png"):
        app.setWindowIcon(QIcon("icon.png"))
    
    window = WallpaperApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
