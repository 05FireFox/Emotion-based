from flask import Flask, request
from flask_cors import CORS
import os
import base64
import uuid  # Added to generate unique filenames
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
    
    # Create a unique filename for this specific request
    unique_filename = f"temp_face_{uuid.uuid4().hex}.png"
    
    # Save the image temporarily
    with open(unique_filename, "wb") as fh:
        fh.write(base64.decodebytes(image_bytes))
    
    try:
        # enforce_detection=True will cause a ValueError if the face is blurry, unstable, or missing
        face_analysis = DeepFace.analyze(
            img_path = unique_filename, 
            actions = ['emotion'],
            enforce_detection = True 
        )

        # Handle case where list is returned
        result = face_analysis[0] if isinstance(face_analysis, list) else face_analysis

        return {'emotion': result['dominant_emotion']}
        
    except ValueError:
        # If DeepFace cannot detect a clear face, it triggers this exception
        return {'emotion': 'undetected', 'message': 'Face blurry or not found'}
        
    except Exception as e:
        # Catch any other unexpected errors
        return {'emotion': 'undetected', 'message': str(e)}
        
    finally:
        # ALWAYS clean up the temporary file, even if DeepFace crashes
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

if __name__ == '__main__':
    # Run on port assigned by Render, turn debug OFF for production
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
