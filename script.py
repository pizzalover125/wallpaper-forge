import sys, os, json, subprocess
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests # type: ignore 
from textwrap import wrap

CONFIG_PATH = os.path.expanduser("~/.wallpaper_forge_config.json")
DEFAULT_CONFIG = {
    "show_message": True,
    "time_display": "Time",
    "show_weather": True,
    "weather_location": "Phoenix,AZ",
    "image_source": "Picsum",
    "overlay_enabled": True,
    "overlay_color": "#000000",  
    "overlay_opacity": 80,  
    "custom_url": "",
    "message_type": "Greeting",
    "google_font_url": "",
    "font_size_message": 80,  
    "font_size_weather": 60,  
    "font_size_time": 80      
}

class WallpaperForge:
    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wallpaper_dir = os.path.expanduser("~/.wallpaper_forge/")
        os.makedirs(self.wallpaper_dir, exist_ok=True)
        self.imagePath = os.path.join(self.wallpaper_dir, f"wallpaper_{self.timestamp}.png")
        self.width, self.height = 3840, 2160
        self.font_path = os.path.join(self.wallpaper_dir, f"font_{self.timestamp}.ttf")
        self.downloadFont()

    def downloadFont(self):
        font_url = self.config.get("google_font_url", "").strip()
        if font_url.startswith("http"):
            try:
                res = requests.get(font_url, timeout=10)
                if res.status_code == 200:
                    with open(self.font_path, "wb") as f:
                        f.write(res.content)
                    return
            except Exception as e:
                print(f"Failed to download custom font: {e}")
        self.font_path = "/System/Library/Fonts/Helvetica.ttc"

    def getMessage(self):
        msg_type = self.config.get("message_type", "Greeting")
        if msg_type == "Quote":
            try:
                res = requests.get("https://zenquotes.io/api/random", timeout=10)
                if res.status_code == 200:
                    data = res.json()[0]
                    return f'"{data["q"]}"\n– {data["a"]}'
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

    def getWeather(self):
        location = self.config.get("weather_location", "Phoenix,AZ")
        try:
            url = f"https://wttr.in/{location}?format=%C+%t+%h+%w"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            print(f"Error getting weather: {e}")
        return "Weather unavailable"

    def getImage(self, retries=5):
        src = self.config.get("image_source", "Picsum")
        attempt = 0
        while attempt < retries:
            try:
                if src == "Picsum":
                    url = "https://picsum.photos/3840/2160"
                    response = requests.get(url, timeout=10)
                    return Image.open(BytesIO(response.content))
                elif src == "Custom URL":
                    custom_url = self.config.get("custom_url", "")
                    if custom_url:
                        response = requests.get(custom_url, timeout=10)
                        return Image.open(BytesIO(response.content))
            except Exception as e:
                print(f"Error loading image (attempt {attempt+1}): {e}")
                attempt += 1
        return None

    def createFallbackBackground(self):
        return Image.new("RGB", (self.width, self.height), (20, 40, 60))

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

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 0, 0) 

    def fit_text(self, draw, text, font_path, max_width, max_height, max_font_size=160, min_font_size=30):
        for size in range(max_font_size, min_font_size - 1, -5):
            try:
                font = ImageFont.truetype(font_path, size)
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
        return ImageFont.truetype(font_path, min_font_size), wrap(text, width=40)

    def generateWallpaper(self):
        img = self.getImage() or self.createFallbackBackground()
        img = img.resize((self.width, self.height))
    
        if self.config.get("overlay_enabled", True):
            overlay_color = self.config.get("overlay_color", "#000000")
            overlay_opacity = self.config.get("overlay_opacity", 80)
            rgb_color = self.hex_to_rgb(overlay_color)
            overlay = Image.new("RGBA", img.size, (*rgb_color, overlay_opacity))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        
        draw = ImageDraw.Draw(img)

        message_font_size = self.config.get("font_size_message", 80)
        weather_font_size = self.config.get("font_size_weather", 60)
        time_font_size = self.config.get("font_size_time", 80)

        base_font = ImageFont.truetype(self.font_path, message_font_size)
        weather_font = ImageFont.truetype(self.font_path, weather_font_size)

        if self.config["show_message"]:
            text = self.getMessage()
            font, wrapped_lines = self.fit_text(draw, text, self.font_path, self.width - 200, self.height // 3, max_font_size=message_font_size, min_font_size=20)
            x = 100
            y = self.height // 2 - (len(wrapped_lines) * (font.getbbox("A")[3] + 10)) // 2
            for line in wrapped_lines:
                draw.text((x + 2, y + 2), line, font=font, fill="black")
                draw.text((x, y), line, font=font, fill="white")
                y += font.getbbox("A")[3] + 10

        if self.config.get("show_weather", True):
            weather_text = self.getWeather()
            weather_font = ImageFont.truetype(self.font_path, weather_font_size)
            x, y = 100, self.height - 200
            draw.text((x + 2, y + 2), weather_text, font=weather_font, fill="black")
            draw.text((x, y), weather_text, font=weather_font, fill="white")

        display = self.config.get("time_display", "Time")
        x = self.width - 600
        y = 100
        if display in ("Time", "Both"):
            now = datetime.now().strftime("%I:%M %p")
            font, lines = self.fit_text(draw, now, self.font_path, 500, 200, max_font_size=time_font_size, min_font_size=20)
            for line in lines:
                draw.text((x + 2, y + 2), line, font=font, fill="black")
                draw.text((x, y), line, font=font, fill="white")
                y += font.getbbox("A")[3] + 10
        if display in ("Date", "Both"):
            today = datetime.now().strftime("%A, %b %d")
            font, lines = self.fit_text(draw, today, self.font_path, 500, 200, max_font_size=time_font_size, min_font_size=20)
            for line in lines:
                draw.text((x + 2, y + 2), line, font=font, fill="black")
                draw.text((x, y), line, font=font, fill="white")
                y += font.getbbox("A")[3] + 10

        img.save(self.imagePath)
        self.cleanupOldWallpapers()
        return self.imagePath

    def setWallpaper(self):
        path = self.imagePath
        if sys.platform.startswith("darwin"):
            script = f'tell application "System Events"\n  tell every desktop\n    set picture to "{path}"\n  end tell\nend tell'
            subprocess.run(["osascript", "-e", script])
        elif sys.platform.startswith("linux"):
            subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{path}"])
        elif sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

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
    except Exception as e:
        print(f"Could not create config: {e}")
    return DEFAULT_CONFIG.copy()

def main():
    try:
        config = load_config()
        forge = WallpaperForge(config)
        print("Generating wallpaper...")
        wallpaper_path = forge.generateWallpaper()
        print(f"Wallpaper generated: {wallpaper_path}")
        print("Setting wallpaper...")
        forge.setWallpaper()
        print("Wallpaper set successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()