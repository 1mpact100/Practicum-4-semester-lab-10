import io
import os

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from huggingface_hub import InferenceClient
from PIL import Image


load_dotenv()

app = Flask(__name__)

MODEL_ID = "black-forest-labs/FLUX.1-schnell"
MIN_SIZE = 256
MAX_SIZE = 1024
JPEG_QUALITY = 88


@app.get("/login")
def login():
    return jsonify({"author": "1160491"})


@app.get("/makeimage")
def makeimage_form():
    return render_template("makeimage.html", message=None)


@app.post("/makeimage")
def makeimage_submit():
    width_raw = request.form.get("width", "")
    height_raw = request.form.get("height", "")
    text = request.form.get("text", "").strip()

    try:
        width = int(width_raw)
        height = int(height_raw)
    except ValueError:
        return render_makeimage_error("Invalid image size")

    if width <= 0 or height <= 0:
        return render_makeimage_error("Invalid image size")

    if width % 32 != 0 or height % 32 != 0:
        return render_makeimage_error("Width and height must be multiples of 32")

    if width < MIN_SIZE or height < MIN_SIZE or width > MAX_SIZE or height > MAX_SIZE:
        return render_makeimage_error("Invalid image size")

    if not text:
        return render_makeimage_error("Model generation failed: prompt is empty")

    token = os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        return render_makeimage_error("Model generation failed: Hugging Face API token is not configured")

    try:
        image = generate_image(text, width, height, token)
        jpeg_bytes = image_to_jpeg(image, width, height)
    except Exception as exc:
        return render_makeimage_error(f"Model generation failed: {exc}")

    return Response(jpeg_bytes, mimetype="image/jpeg")


def render_makeimage_error(message):
    return render_template(
        "makeimage.html",
        message=message,
        width=request.form.get("width", ""),
        height=request.form.get("height", ""),
        text=request.form.get("text", ""),
    )


def generate_image(prompt, width, height, token):
    client = InferenceClient(model=MODEL_ID, token=token, timeout=30)

    try:
        result = client.text_to_image(prompt, width=width, height=height)
    except TypeError:
        result = client.text_to_image(prompt)

    if isinstance(result, Image.Image):
        return result

    if isinstance(result, bytes):
        return Image.open(io.BytesIO(result))

    if hasattr(result, "read"):
        return Image.open(result)

    raise RuntimeError("unexpected response from model")


def image_to_jpeg(image, width, height):
    if image.size != (width, height):
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    if image.mode != "RGB":
        image = image.convert("RGB")

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=JPEG_QUALITY)
    return output.getvalue()


if __name__ == "__main__":
    app.run(debug=True)
