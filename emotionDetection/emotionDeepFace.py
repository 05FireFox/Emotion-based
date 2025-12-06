from flask import Flask, request
from flask_cors import CORS
import os
import base64
from deepface import DeepFace

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/emotion', methods=['POST'])
def get_polarity():
    requestJson = request.get_json(force=True)
    image_string = requestJson['image']
    
    # Extract the base64 part
    image_bytes = bytes(image_string.split(',')[1], 'UTF-8')
    
    # Save the image temporarily
    with open("imageToSave.png", "wb") as fh:
        fh.write(base64.decodebytes(image_bytes))
    
    # FIX APPLIED HERE: Added actions=['emotion']
    # This tells DeepFace to skip downloading Age, Gender, and Race models.
    # enforce_detection=False prevents crash if face isn't perfect.
    face_analysis = DeepFace.analyze(
        img_path = "imageToSave.png", 
        actions = ['emotion'],
        enforce_detection = False
    )

    # Handle case where list is returned
    result = face_analysis[0] if isinstance(face_analysis, list) else face_analysis

    return {'emotion': result['dominant_emotion']}

if __name__ == '__main__':
    # Run on port 8080 (Docker default)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))