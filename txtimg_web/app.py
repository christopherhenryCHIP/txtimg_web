import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Paths
FONT_PATH = os.path.join("fonts", "arial bold.ttf")
WIDTH = 1320
HEIGHT = 2868

# Image generation function
def generate_image(text):
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)

    # Font size relative to canvas width
    font_size = int(WIDTH * 0.09)
    font = ImageFont.truetype(FONT_PATH, size=font_size)

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Measure multiline text block
    bbox = draw.multiline_textbbox(
        (0, 0), text, font=font, spacing=int(font_size*0.4), align="center"
    )
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center block
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2

    # Draw blue text
    draw.multiline_text(
        (x, y), text, font=font, fill=(0, 0, 255, 255),
        spacing=int(font_size*0.4), align="center"
    )

    # Save to BytesIO
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Route for form and image generation
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text", "LINE ONE\nLINE TWO\nLINE THREE")
        return send_file(generate_image(text), mimetype="image/png")
    return render_template("index.html")

# Production port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
