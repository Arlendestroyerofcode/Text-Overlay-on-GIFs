from flask import Flask, request, jsonify, send_from_directory, render_template
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import numpy as np
import os
from ultralytics import YOLO
import cv2
import textwrap

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

FONT_SIZE = 30
MAX_FONT_SCALE = 1.0
MIN_FONT_SCALE = 0.4
FONT_THICKNESS = 4
FONT_PATH = "C:/Windows/Fonts/arial.ttf"
TEXT_COLOR = (0, 0, 0, 150)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

# Load YOLO model
model = YOLO("runs/detect/train11/weights/best.pt")

# List of clothing classes
clothing_classes = ['shirt', 'sweater', 't-shirt'] #skirt, pants, sweater

def detect_clothing_regions_with_yolo(frame):
    if frame.mode == "RGBA":
        frame = frame.convert("RGB")
    
    frame_array = np.array(frame)
    
    # Run YOLO model
    results = model.predict(frame_array, conf=0.5, device="cpu")

    detected_regions = []
    if results and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            class_id = int(box.cls.item())
            class_name = model.names[class_id]
            if class_name in clothing_classes:
                detected_regions.append(box.xyxy.tolist())

    return detected_regions

# Initialize MedianFlow tracker
tracker = cv2.legacy.TrackerMedianFlow_create()
tracking_initialized = False
bbox = None  # Bounding box of tracked clothing

def find_largest_open_space(bbox, frame_size, aspect_ratio_threshold=2.0):
    """ Expand downward only if the object is tall enough, otherwise center text. """
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1

    center_x = x1 + w // 2
    center_y = y1 + h // 2

    # Calculate aspect ratio (width/height)
    aspect_ratio = w / h  

    if aspect_ratio < aspect_ratio_threshold:  
        # If it's **tall**, expand downward
        new_y = min(center_y + int(h * 0.15), y2 - 20)
    else:
        # If it's **wide**, just center text in the middle of the banner
        new_y = center_y  

    return center_x, new_y

def fit_text_to_bbox(text, bbox, font_size=FONT_SIZE, max_font_scale=MAX_FONT_SCALE, min_font_scale=MIN_FONT_SCALE, font_thickness=FONT_THICKNESS):
    """ Adjust text to fit inside bounding box by scaling or wrapping into multiple lines. """
    
    x1, y1, x2, y2 = bbox
    max_width = x2 - x1
    max_height = y2 - y1

    font = ImageFont.truetype(FONT_PATH, font_size)
    scale = max_font_scale
    text_bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)

    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Reduce text size if it overflows
    while text_width > max_width and scale > min_font_scale:
        scale -= 0.05  # Use a smaller step for scaling
        font = ImageFont.truetype(FONT_PATH, int(font_size * scale))
        text_bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # If scaling down reaches limit, wrap text into multiple lines
    if text_width > max_width:
        words_per_line = max_width // (text_width // len(text))
        wrapped_text = textwrap.fill(text, width=words_per_line)
        return wrapped_text, scale
    else:
        return text, scale

def add_text_on_clothing(frame, text, detected_region, font_size=30):
    global tracker, tracking_initialized, bbox

    frame_array = np.array(frame)

    if not tracking_initialized:
        if detected_region:
            for bbox_coords in detected_region:
                bbox_coords = np.array(bbox_coords).flatten()
                x1, y1, x2, y2 = map(int, bbox_coords)

                # Expand the box downward to capture more space
                y2 = min(y2 + int((y2 - y1) * 0.2), frame.size[1])

                bbox = (x1, y1, x2 - x1, y2 - y1)
                tracker.init(frame_array, bbox)
                tracking_initialized = True
                break

    else:
        success, bbox = tracker.update(frame_array)
        if success:
            # Extract the updated bbox (x, y, w, h)
            x, y, w, h = [int(v) for v in bbox]

            # Ensure the variables are available for text positioning
            x1, y1, x2, y2 = x, y, x + w, y + h

            # Limit text width of the container's width
            max_text_width = (x2 - x1) * 0.6
            wrapped_text, new_scale = fit_text_to_bbox(text, (x1, y1, x2, y2), font_size)

            # Create a blank transparent text layer
            text_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))  # Make sure it's the same size as the frame
            draw = ImageDraw.Draw(text_layer)

            y_offset = 0
            x_offset = 0
            for line in wrapped_text.split("\n"):
                # Calculate the text bounding box
                text_bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), line, font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(font_size * new_scale)))
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

                # Ensure text width doesn't exceed max allowed width
                if text_width > max_text_width:
                    new_scale *= (max_text_width / text_width)

                # Recalculate the text size with the adjusted scale
                text_bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), line, font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(font_size * new_scale)))
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

                # Align text to the bottom of the bounding box
                text_y = y2 - text_height - y_offset - 40  # Add px padding at the bottom
                text_x = x + (w - text_width) // 2 - x_offset + 10  # Center text horizontally within the bounding box (+10 is an initial shift to the right. Can break tracking)

                # Prevent text from going out of bounds horizontally
                if text_x < x:
                    text_x = x
                if text_x + text_width > x2:
                    text_x = x2 - text_width

                # Draw the text
                draw.text((text_x, text_y), line, font=ImageFont.truetype(FONT_PATH, int(font_size * new_scale)), fill=(0, 0, 0, 150))
                y_offset += text_height + 5  # Space between lines

            # Resize text_layer to match the size of the frame
            text_layer = text_layer.resize(frame.size, Image.Resampling.LANCZOS)

            # Composite the text onto the frame
            frame = Image.alpha_composite(frame.convert("RGBA"), text_layer)

    return frame

@app.route('/process', methods=['POST'])
def process_gif():
    gif = request.files['gif']
    text = request.form['text']

    gif_path = os.path.join(app.config['UPLOAD_FOLDER'], gif.filename)
    gif.save(gif_path)

    original_gif = Image.open(gif_path)
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(original_gif):
        frame = frame.convert("RGBA")
        detected_region = detect_clothing_regions_with_yolo(frame)
        frame = add_text_on_clothing(frame, text, detected_region)

        frames.append(frame)
        durations.append(frame.info.get("duration", 100))

    processed_gif_path = os.path.join(app.config['PROCESSED_FOLDER'], gif.filename)
    frames[0].save(processed_gif_path, save_all=True, append_images=frames[1:], loop=0, duration=durations)

    return jsonify({"filename": gif.filename})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)