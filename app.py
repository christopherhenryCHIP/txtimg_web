import os
import io
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# ---- constants ----
WIDTH = 1320
HEIGHT = 2868

FONT_DIR = "fonts"
FONTS = {
    "arial": os.path.join(FONT_DIR, "arial bold.ttf"),
    "times": os.path.join(FONT_DIR, "times new roman.ttf"),
}

DEFAULT_FONT = "arial"

# ---- helpers ----
def hex_to_rgb(hex_color):
    try:
        hex_color = hex_color.strip().lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (0, 0, 0)

def generate_image(
    text,
    font_key,
    text_color="#000000",
    bg_color="#f5f0e6",
    text_size_percent=0.12,
    text_alpha=255,
    bg_alpha=255
):
    # ---- font selection (locked) ----
    font_path = FONTS.get(font_key, FONTS[DEFAULT_FONT])

    # ---- background ----
    bg_rgba = hex_to_rgb(bg_color) + (bg_alpha,)
    image = Image.new("RGBA", (WIDTH, HEIGHT), bg_rgba)

    # ---- text layer ----
    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    font_size = max(1, int(WIDTH * text_size_percent))
    font = ImageFont.truetype(font_path, font_size)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=int(font_size * 0.4),
        align="center"
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2

    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=hex_to_rgb(text_color) + (text_alpha,),
        spacing=int(font_size * 0.4),
        align="center"
    )

    image = Image.alpha_composite(image, text_layer)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ---- routes ----
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text", "")
        font_key = request.form.get("font", DEFAULT_FONT)

        text_color = request.form.get("text_color", "#000000")
        bg_color = request.form.get("bg_color", "#f5f0e6")

        try:
            text_size_percent = int(request.form.get("text_size", 12)) / 100
        except Exception:
            text_size_percent = 0.12

        try:
            text_alpha = int(int(request.form.get("text_alpha", 100)) * 255 / 100)
        except Exception:
            text_alpha = 255

        try:
            bg_alpha = int(int(request.form.get("bg_alpha", 100)) * 255 / 100)
        except Exception:
            bg_alpha = 255

        return send_file(
            generate_image(
                text=text,
                font_key=font_key,
                text_color=text_color,
                bg_color=bg_color,
                text_size_percent=text_size_percent,
                text_alpha=text_alpha,
                bg_alpha=bg_alpha
            ),
            mimetype="image/png"
        )

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
