import sys, os, json, subprocess
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests # type: ignore 
from textwrap import wrap
import numpy as np # type: ignore

# set constants
CONFIG_PATH = os.path.expanduser("~/.wallpaper_forge_config.json")
DEFAULT_CONFIG = { 
    "show_message": True,
    "time_display": "Time",
    "show_weather": True,
    "weather_location": "Phoenix,AZ",
    "image_source": "Custom URL",
    "overlay_enabled": True,
    "overlay_color": "#000000",  
    "overlay_opacity": 80,  
    "custom_url": "",
    "message_type": "Greeting",
    "custom_message": "",  
    "google_font_url": "",
    "font_size_message": 80,  
    "font_size_weather": 60,  
    "font_size_time": 80,
    "filters_enabled": True,
    "blur_enabled": False,
    "blur_intensity": 2,
    "brightness": 100,  
    "contrast": 100, 
    "saturation": 100,  
    "sharpness": 100,   
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

# main class
class WallpaperForge:
    # initalizes with config 
    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wallpaper_dir = os.path.expanduser("~/.wallpaper_forge/")
        os.makedirs(self.wallpaper_dir, exist_ok=True)
        self.imagePath = os.path.join(self.wallpaper_dir, f"wallpaper_{self.timestamp}.png")
        self.width, self.height = 3840, 2160
        self.font_path = os.path.join(self.wallpaper_dir, f"font_{self.timestamp}.ttf")
        print("Downloading font...")
        self.downloadFont()

    # downloads the font from Google Fonts or uses system default (this seems to be buggy on Windows) 
    def downloadFont(self):
        font_url = self.config.get("google_font_url", "").strip() 
        if font_url.startswith("http"):
            try:
                print(f"Fetching font from: {font_url}")
                res = requests.get(font_url, timeout=10)
                if res.status_code == 200:
                    with open(self.font_path, "wb") as f:
                        f.write(res.content)
                    print("Font downloaded successfully")
                    return
                else:
                    print(f"Font download failed with status: {res.status_code}")
            except Exception as e:
                print(f"Failed to download custom font: {e}")

        if sys.platform.startswith("darwin"):
            self.font_path = "/System/Library/Fonts/Helvetica.ttc"
        elif sys.platform.startswith("linux"):
            possible_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
            for font in possible_fonts:
                if os.path.exists(font):
                    self.font_path = font
                    break
            else:
                self.font_path = None  
        else: 
            self.font_path = "C:/Windows/Fonts/arial.ttf"
        
        print(f"Using font: {self.font_path}")

    # retrieves the message based on config settings
    def getMessage(self):
        msg_type = self.config.get("message_type", "Greeting")
        print(f"Getting message type: {msg_type}")
        
        if msg_type == "Custom":
            custom_msg = self.config.get("custom_message", "").strip()
            if custom_msg:
                return custom_msg
            else:
                return "Custom message not set"
        elif msg_type == "Quote":
            try:
                print("Fetching quote...")
                res = requests.get("https://zenquotes.io/api/random", timeout=5)
                if res.status_code == 200:
                    data = res.json()[0]
                    quote = f'"{data["q"]}"\n– {data["a"]}'
                    print("Quote fetched successfully")
                    return quote
                else:
                    print(f"Quote API returned status: {res.status_code}")
            except Exception as e:
                print(f"Error fetching quote: {e}")
            return "Quote unavailable"
        else: 
            hour = datetime.now().hour
            if 0 < hour < 5:
                return "Go to sleep!!"
            elif 5 <= hour < 12:
                return "Have a good morning!"
            elif 12 <= hour < 18:
                return "Have a good afternoon!"
            elif 18 <= hour < 22:
                return "Have a good evening!"
            else:
                return "Have a good night!"

    # retrieves weather from wttr.in API if selected
    def getWeather(self):
        location = self.config.get("weather_location", "Phoenix,AZ")
        print(f"Getting weather for: {location}")
        try:
            url = f"https://wttr.in/{location}?format=%C+%t+%h"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather = response.text.strip()
                print(f"Weather: {weather}")
                return weather
            else:
                print(f"Weather API returned status: {response.status_code}")
        except Exception as e:
            print(f"Error getting weather: {e}")
        return "Weather unavailable"

    # retrieves image from configured source
    # retries up to 3 times if download fails
    def getImage(self, retries=3):
        src = self.config.get("image_source", "Picsum")
        print(f"Getting image from source: {src}")
        attempt = 0
        while attempt < retries:
            try:
                if "Picsum" in src or src == "Picsum":
                    url = "https://picsum.photos/3840/2160"
                    print(f"Fetching image from Picsum (attempt {attempt+1})...")
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        print("Image downloaded successfully")
                        return Image.open(BytesIO(response.content))
                    else:
                        print(f"Image download failed with status: {response.status_code}")
                elif "Custom" in src or src == "Custom URL":
                    custom_url = self.config.get("custom_url", "")
                    if custom_url.strip():
                        print(f"Fetching image from custom URL: {custom_url}")
                        response = requests.get(custom_url.strip(), timeout=15)
                        if response.status_code == 200:
                            print("Custom image downloaded successfully")
                            return Image.open(BytesIO(response.content))
                        else:
                            print(f"Custom image download failed with status: {response.status_code}")
                    else:
                        print("No custom URL provided, trying Picsum as fallback")
                        url = "https://picsum.photos/3840/2160"
                        print(f"Fetching fallback image from Picsum (attempt {attempt+1})...")
                        response = requests.get(url, timeout=15)
                        if response.status_code == 200:
                            print("Fallback image downloaded successfully")
                            return Image.open(BytesIO(response.content))
                else:
                    print(f"Unknown image source '{src}', defaulting to Picsum")
                    url = "https://picsum.photos/3840/2160"
                    print(f"Fetching image from Picsum (attempt {attempt+1})...")
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        print("Image downloaded successfully")
                        return Image.open(BytesIO(response.content))
                    else:
                        print(f"Image download failed with status: {response.status_code}")
            except Exception as e:
                print(f"Error loading image (attempt {attempt+1}): {e}")
                attempt += 1
        
        print("All image download attempts failed, using fallback")
        return None

    # creates a fallback background if image retrieval fails
    def createFallbackBackground(self):
        print("Creating fallback background")
        return Image.new("RGB", (self.width, self.height), (20, 40, 60))

    # applies filters based on config settings using PIL + numpy
    def applyImageFilters(self, img):
        if not self.config.get("filters_enabled", True):
            return img
        
        print("Applying image filters...")
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if self.config.get("brightness", 100) != 100:
            enhancer = ImageEnhance.Brightness(img)
            factor = self.config.get("brightness", 100) / 100.0
            img = enhancer.enhance(factor)
            print(f"Applied brightness: {factor}")
        
        if self.config.get("contrast", 100) != 100:
            enhancer = ImageEnhance.Contrast(img)
            factor = self.config.get("contrast", 100) / 100.0
            img = enhancer.enhance(factor)
            print(f"Applied contrast: {factor}")
        
        if self.config.get("saturation", 100) != 100:
            enhancer = ImageEnhance.Color(img)
            factor = self.config.get("saturation", 100) / 100.0
            img = enhancer.enhance(factor)
            print(f"Applied saturation: {factor}")
        
        if self.config.get("sharpness", 100) != 100:
            enhancer = ImageEnhance.Sharpness(img)
            factor = self.config.get("sharpness", 100) / 100.0
            img = enhancer.enhance(factor)
            print(f"Applied sharpness: {factor}")
        
        if self.config.get("blur_enabled", False):
            radius = self.config.get("blur_intensity", 2)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
            print(f"Applied blur: radius {radius}")
        
        if self.config.get("edge_enhance_enabled", False):
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            print("Applied edge enhance")
        
        if self.config.get("emboss_enabled", False):
            img = img.filter(ImageFilter.EMBOSS)
            print("Applied emboss")
        
        if self.config.get("grayscale_enabled", False):
            img = img.convert('L').convert('RGB')
            print("Applied grayscale")
        
        if self.config.get("sepia_enabled", False):
            img = self.applySepia(img)
            print("Applied sepia")
        
        if self.config.get("invert_enabled", False):
            img_array = np.array(img)
            img_array = 255 - img_array
            img = Image.fromarray(img_array)
            print("Applied invert")
        
        if self.config.get("posterize_enabled", False):
            bits = self.config.get("posterize_bits", 4)
            img = img.quantize(colors=2**bits).convert('RGB')
            print(f"Applied posterize: {bits} bits")

        if self.config.get("vintage_enabled", False):
            img = self.applyVintage(img)
            print("Applied vintage effect")
        
        if self.config.get("vignette_enabled", False):
            img = self.applyVignette(img)
            print("Applied vignette")
        
        if self.config.get("noise_enabled", False):
            img = self.addNoise(img)
            print("Applied noise")
        
        return img
    
    # applies sepia filter using numpy
    def applySepia(self, img):
        img_array = np.array(img, dtype=np.float32)
        
        sepia_filter = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        sepia_img = img_array @ sepia_filter.T
        sepia_img = np.clip(sepia_img, 0, 255)
        
        return Image.fromarray(sepia_img.astype(np.uint8))
    
    # applies vintage effect using PIL
    def applyVintage(self, img):
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        
        overlay = Image.new('RGB', img.size, (255, 220, 177))  
        intensity = self.config.get("vintage_intensity", 50) / 100.0
        
        img = Image.blend(img, overlay, intensity * 0.2)
        
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return img
    
    # applies vignette effect using numpy
    def applyVignette(self, img):
        width, height = img.size
        intensity = self.config.get("vignette_intensity", 50) / 100.0
        
        vignette = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(vignette)
        
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        for i in range(50): 
            alpha = int(255 * (1 - (i / 50) * intensity))
            radius_x = int(max_radius * (1 + i * 0.02))
            radius_y = int(max_radius * (1 + i * 0.02))
            
            bbox = [
                center_x - radius_x, center_y - radius_y,
                center_x + radius_x, center_y + radius_y
            ]
            draw.ellipse(bbox, fill=alpha)
        
        img_array = np.array(img)
        vignette_array = np.array(vignette) / 255.0
        
        for c in range(3):  
            img_array[:, :, c] = img_array[:, :, c] * vignette_array
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    # adds noise to the image using numpy
    def addNoise(self, img):
        img_array = np.array(img, dtype=np.float32)
        intensity = self.config.get("noise_intensity", 25)
        
        noise = np.random.normal(0, intensity, img_array.shape)
        
        noisy_img = img_array + noise
        noisy_img = np.clip(noisy_img, 0, 255)
        
        return Image.fromarray(noisy_img.astype(np.uint8))

    # deletes old wallpapers except the current one
    def cleanupOldWallpapers(self):
        try:
            wallpaper_files = [f for f in os.listdir(self.wallpaper_dir) if f.startswith("wallpaper_")]
            for filename in wallpaper_files:
                if not filename.endswith(self.timestamp + ".png"):
                    try:
                        os.remove(os.path.join(self.wallpaper_dir, filename))
                    except OSError as e:
                        print(f"Could not delete {filename}: {e}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    # helper function to convert hex color to RGB
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 0, 0) 

    # fits text to the image size, returns font and wrapped lines
    def fit_text(self, draw, text, font_path, max_width, max_height, max_font_size=160, min_font_size=30):
        for size in range(max_font_size, min_font_size - 1, -5):
            try:
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, size)
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            lines = []
            for paragraph in text.split('\n'):
                lines.extend(wrap(paragraph, width=40))
            line_height = font.getbbox("A")[3] + 10
            total_height = line_height * len(lines)
            max_line_width = max(draw.textlength(line, font=font) for line in lines)
            if total_height <= max_height and max_line_width <= max_width:
                return font, lines
        return ImageFont.load_default(), wrap(text, width=40)

    # calculates the x position for text to fit within the image width
    def calculate_text_position(self, draw, text_lines, font, margin=100):
        if not text_lines:
            return self.width - margin

        max_line_width = max(draw.textlength(line, font=font) for line in text_lines)
        x_position = self.width - max_line_width - margin
        return max(margin, x_position)

    # generates the wallpaper with all components
    def generateWallpaper(self):
        print("Starting wallpaper generation...")
        
        img = self.getImage() or self.createFallbackBackground()
        print("Resizing image...")
        img = img.resize((self.width, self.height))

        img = self.applyImageFilters(img)
    
        if self.config.get("overlay_enabled", True):
            print("Applying overlay...")
            overlay_color = self.config.get("overlay_color", "#000000")
            overlay_opacity = self.config.get("overlay_opacity", 80)
            rgb_color = self.hex_to_rgb(overlay_color)
            overlay = Image.new("RGBA", img.size, (*rgb_color, overlay_opacity))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        
        draw = ImageDraw.Draw(img)

        message_font_size = self.config.get("font_size_message", 80)
        weather_font_size = self.config.get("font_size_weather", 60)
        time_font_size = self.config.get("font_size_time", 80)

        if self.config.get("show_message", False):
            print("Adding message text...")
            text = self.getMessage()
            try:
                if self.font_path and os.path.exists(self.font_path):
                    message_font = ImageFont.truetype(self.font_path, message_font_size)
                else:
                    message_font = ImageFont.load_default()
            except:
                message_font = ImageFont.load_default()
            
            lines = []
            for paragraph in text.split('\n'):
                lines.extend(wrap(paragraph, width=40))
            
            x = 100
            line_height = message_font.getbbox("A")[3] + 10
            y = self.height // 2 - (len(lines) * line_height) // 2
            
            for line in lines:
                draw.text((x + 2, y + 2), line, font=message_font, fill="black")
                draw.text((x, y), line, font=message_font, fill="white")
                y += line_height

        if self.config.get("show_weather", True):
            print("Adding weather text...")
            weather_text = self.getWeather()
            try:
                if self.font_path and os.path.exists(self.font_path):
                    weather_font = ImageFont.truetype(self.font_path, weather_font_size)
                else:
                    weather_font = ImageFont.load_default()
            except:
                weather_font = ImageFont.load_default()
            x, y = 100, self.height - 200
            draw.text((x + 2, y + 2), weather_text, font=weather_font, fill="black")
            draw.text((x, y), weather_text, font=weather_font, fill="white")

        if self.config.get("show_time", True): 
            print("Adding time/date text...")
            display = self.config.get("time_display", "Time")
            y = 100
            
            time_lines = []
            
            if display in ("Time", "Both"):
                now = datetime.now().strftime("%I:%M %p")
                time_lines.extend(wrap(now, width=40))
                
            if display in ("Date", "Both"):
                today = datetime.now().strftime("%A, %b %d")
                time_lines.extend(wrap(today, width=40))
            
            if time_lines:
                try:
                    if self.font_path and os.path.exists(self.font_path):
                        time_font = ImageFont.truetype(self.font_path, time_font_size)
                    else:
                        time_font = ImageFont.load_default()
                except:
                    time_font = ImageFont.load_default()
                
                x = self.calculate_text_position(draw, time_lines, time_font, margin=100)
                
                current_y = y
                if display in ("Time", "Both"):
                    now = datetime.now().strftime("%I:%M %p")
                    lines = wrap(now, width=40)
                    for line in lines:
                        draw.text((x + 2, current_y + 2), line, font=time_font, fill="black")
                        draw.text((x, current_y), line, font=time_font, fill="white")
                        current_y += time_font.getbbox("A")[3] + 10
                        
                if display in ("Date", "Both"):
                    today = datetime.now().strftime("%A, %b %d")
                    lines = wrap(today, width=40)
                    for line in lines:
                        draw.text((x + 2, current_y + 2), line, font=time_font, fill="black")
                        draw.text((x, current_y), line, font=time_font, fill="white")
                        current_y += time_font.getbbox("A")[3] + 10

        print("Saving wallpaper...")
        img.save(self.imagePath)
        print("Cleaning up old wallpapers...")
        self.cleanupOldWallpapers()
        return self.imagePath

    # sets wallpaper based on the platform
    # uses AppleScript for macOS, gnome for Linux, and ctypes for Windows
    def setWallpaper(self):
        path = self.imagePath
        print(f"Setting wallpaper: {path}")
        if sys.platform.startswith("darwin"):
            script = f'tell application "System Events"\n  tell every desktop\n    set picture to "{path}"\n  end tell\nend tell'
            subprocess.run(["osascript", "-e", script])
        elif sys.platform.startswith("linux"):
            subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{path}"])
        elif sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

# loads config from file or creates default config
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"Created default config at: {CONFIG_PATH}")
    except Exception as e:
        print(f"Could not create config: {e}")
    return DEFAULT_CONFIG.copy()

# main function to run the wallpaper generation (w/ debug printing!)
def main():
    try:
        print("Loading configuration...")
        config = load_config()
        print(f"Configuration loaded: {config}")
        
        forge = WallpaperForge(config)
        print("Generating wallpaper...")
        wallpaper_path = forge.generateWallpaper()
        print(f"Wallpaper generated: {wallpaper_path}")
        print("Setting wallpaper...")
        forge.setWallpaper()
        print("Wallpaper set successfully!")
    except Exception as e: 
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()