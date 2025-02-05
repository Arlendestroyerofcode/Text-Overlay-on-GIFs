Text Overlay on GIFs
Overview
This project provides a simple way for users to upload a GIF, add text, and download the modified GIF with the text applied. The primary goal is to create an interactive tool that allows easy customization of GIFs by overlaying custom text onto each frame of the GIF. This can be used for creating personalized GIFs with messages, captions, or other forms of text that move with the animation.

Features
GIF Upload: Users can upload a GIF to the platform.
Text Input: Users can enter custom text to overlay onto the GIF.
Text Overlay: The text is added to the GIF's frames, ensuring it moves with the GIF's animation.
Download Option: Once the GIF is processed, users can download the modified GIF with the text applied. (Note: The specific functionality to allow downloads is currently broken. The send_from_directory function was intended to handle this task, but that part of the code was lost during creation. It will be fixed soon.)
Custom Dataset
For the text overlay functionality, a custom dataset was used due to the limitations of available sources. Many pre-existing datasets either didn’t provide acceptable results or had functionality issues that prevented them from being effective in this case. As such, a tailored dataset was created to achieve the desired results. (Note: While the custom dataset has shown satisfactory results, it's not perfect, and some retraining may be needed for optimal performance.)

How It Works
Key Libraries Used:
Flask: Used as the web framework for creating the interface and handling requests.
Pillow: Used for working with image files, especially for overlaying the text on GIF frames.
NumPy: Used for handling arrays and matrix operations, which are essential when manipulating image pixels.
Ultralytics YOLO: Used for object detection in frames (optional feature depending on how you want to process GIFs further).
OpenCV: For additional image and video processing needs.
Textwrap: Used to wrap long text so that it fits neatly onto the frames of the GIF.
Workflow:
User uploads a GIF: The app receives the GIF file and processes it.
User enters text: The user can specify the text to overlay.
Text is applied: The code loops through each frame of the GIF, overlays the entered text on it, and compiles the frames back into a GIF.
Download the result: Once the processing is complete, the modified GIF is available for download.
Code Explanation:
The code takes advantage of Flask for handling web requests, Pillow for image manipulation, and OpenCV for video processing. Each frame of the GIF is processed individually, with the text being rendered and added using PIL (Python Imaging Library). The final frames are then compiled into a new GIF, maintaining the animation.

Installation
To get started with this project, clone the repository and install the required dependencies.

bash
Copy
Edit
git clone <repository_url>
cd <project_directory>
pip install -r requirements.txt
Usage
Run the Flask Application:

bash
Copy
Edit
python app.py
Open a browser and navigate to http://127.0.0.1:5000 (or the specified port) to interact with the tool.

Upload your GIF, enter the desired text, and hit "Submit" to apply the text overlay.

Once the process is complete, you can download the modified GIF.

License
This project is licensed under the MIT License.

Acknowledgments
Special thanks to the creators of the following libraries used in this project:
Flask: For building the web application framework.
Pillow: For providing excellent image manipulation tools.
Ultralytics YOLO: For object detection capabilities.
OpenCV: For image processing functionality.