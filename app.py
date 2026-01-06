import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Constants
WIDTH = 1320
HEIGHT = 2868
FONT_PATH = os.path.join("fonts", "arial bold.ttf")

# Helper: hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Image generation
def generate_image(text, text_color="#0000ff", bg_color="#000000",
                   text_size_percent=0.09, text_alpha=255, bg_alpha=255):
    text_rgb = hex_to_rgb(text_color) + (text_alpha,)
    bg_rgb = hex_to_rgb(bg_color) + (bg_alpha,)

    # Create image
    image = Image.new("RGBA", (WIDTH, HEIGHT), bg_rgb)
    draw = ImageDraw.Draw(image)

    # Font size
    font_size = int(WIDTH * text_size_percent)
    font = ImageFont.truetype(FONT_PATH, size=font_size)

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Measure text
    bbox = draw.multiline_textbbox((0,0), text, font=font, spacing=int(font_size*0.4), align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2

    # Draw text
    draw.multiline_text((x, y), text, font=font, fill=text_rgb,
                        spacing=int(font_size*0.4), align="center")

    # Save to buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Flask route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text", "LINE ONE\nLINE TWO\nLINE THREE")
        text_color = request.form.get("text_color", "#0000ff")
        bg_color = request.form.get("bg_color", "#000000")
        text_size_percent = float(request.form.get("text_size", 9)) / 100

        text_alpha = int(request.form.get("text_alpha", 100) * 255 / 100)
        bg_alpha = int(request.form.get("bg_alpha", 100) * 255 / 100)

        return send_file(
            generate_image(
                text, text_color, bg_color,
                text_size_percent, text_alpha, bg_alpha
            ),
            mimetype="image/png"
        )
    return render_template("index.html")

# Render port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
