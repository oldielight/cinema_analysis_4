import cv2
import numpy as np
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EmotionAnalyzerWithMemory:
    def __init__(self):
        self.setup_models()
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.results = []
        self.last_valid_result = None

    def setup_models(self):
        try:
            from deepface import DeepFace
            self.deepface_available = True
        except ImportError:
            self.deepface_available = False

        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            eye_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_path)
            mouth_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            self.mouth_cascade = cv2.CascadeClassifier(mouth_path)
        except Exception:
            pass

    def detect_faces(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def extract_features(self, img, faces):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = {}
        for i, (x, y, w, h) in enumerate(faces):
            roi = gray[y:y+h, x:x+w]
            features[f'face_{i}_brightness'] = float(np.mean(roi))
            features[f'face_{i}_contrast'] = float(np.std(roi))
            features[f'face_{i}_area'] = int(w * h)
            edges = cv2.Canny(roi, 50, 150)
            features[f'face_{i}_edge_density'] = float(np.sum(edges > 0) / (w * h))
            eyes = self.eye_cascade.detectMultiScale(roi)
            features[f'face_{i}_eyes_detected'] = len(eyes)
            smiles = self.mouth_cascade.detectMultiScale(roi)
            features[f'face_{i}_smiles_detected'] = len(smiles)
        return features

    def analyze_deepface(self, image_path, fallback_img=None):
        if not self.deepface_available:
            return None
        from deepface import DeepFace
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion'],
                detector_backend='retinaface',
                enforce_detection=False,
                silent=True
            )
            if isinstance(result, list):
                result = result[0]
            return result['emotion']
        except:
            if fallback_img is not None:
                try:
                    temp_path = "/tmp/cropped_face.jpg"
                    cv2.imwrite(temp_path, fallback_img)
                    result = DeepFace.analyze(
                        img_path=temp_path,
                        actions=['emotion'],
                        detector_backend='retinaface',
                        enforce_detection=False,
                        silent=True
                    )
                    if isinstance(result, list):
                        result = result[0]
                    return result['emotion']
                except:
                    return None
            return None

    def infer_emotion(self, features, deepface_result=None):
        scores = {emotion: 0.0 for emotion in self.emotion_labels}
        if deepface_result:
            for emotion in self.emotion_labels:
                if emotion in deepface_result:
                    scores[emotion] += deepface_result[emotion] * 0.5

        for key, value in features.items():
            if 'smiles_detected' in key and value > 0:
                scores['happy'] += 0.4
            elif 'edge_density' in key and value > 0.15:
                scores['angry'] += 0.2

        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores['neutral'] = 1.0
        return scores

    def default_result(self, image_name, reason):
        return {
            'image_name': image_name,
            'predicted_emotion': 'neutral',
            'confidence': 0.0,
            'emotion_scores': {e: 0.0 for e in self.emotion_labels},
            'faces_detected': 0,
            'timestamp': datetime.now().isoformat(),
            'note': reason
        }

    def analyze_image(self, image_path, image_name):
        img = cv2.imread(image_path)
        if img is None:
            result = self.default_result(image_name, "Image load failed")
            self.results.append(result)
            return result

        faces = self.detect_faces(img)

        if len(faces) > 1:
            faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
            faces = [faces[0]]

        if len(faces) == 0 and self.last_valid_result:
            copied = self.last_valid_result.copy()
            copied.update({
                'image_name': image_name,
                'timestamp': datetime.now().isoformat(),
                'faces_detected': 0,
                'note': 'Face not detected, previous emotion carried over'
            })
            self.results.append(copied)
            return copied

        features = self.extract_features(img, faces)

        fallback_crop = None
        if len(faces) > 0:
            x, y, w, h = faces[0]
            fallback_crop = img[y:y+h, x:x+w]

        deepface_result = self.analyze_deepface(image_path, fallback_crop)
        scores = self.infer_emotion(features, deepface_result)
        predicted = max(scores.items(), key=lambda x: x[1])

        result = {
            'image_name': image_name,
            'predicted_emotion': predicted[0],
            'confidence': predicted[1],
            'emotion_scores': scores,
            'faces_detected': len(faces),
            'timestamp': datetime.now().isoformat()
        }

        self.last_valid_result = result
        self.results.append(result)
        return result

    def analyze_folder(self, folder):
        try:
            current_script_path = os.path.abspath(__file__)
        except NameError:
            current_script_path = os.getcwd()
        script_dir = os.path.dirname(current_script_path)
        
        folder_path = os.path.normpath(os.path.join(script_dir, folder))

        print(f"Analyzing images from: {folder_path}")

        try:
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not files:
                print(f"Warning: No image files found in {folder_path}")
                self.results = []
                return self.results

            for f in sorted(files):
                path = os.path.join(folder_path, f)
                self.analyze_image(path, f)
            return self.results
        except FileNotFoundError:
            print(f"Error: Directory not found at {folder_path}")

    def save_results(self, out_path):
        os.makedirs(out_path, exist_ok=True)
        with open(os.path.join(out_path, 'emotion_results.json'), 'w') as f:
            json.dump(self.results, f, indent=2)

def main():
    input_folder_name = "../data/results/candidates_1"
    relative_output_folder = "../data/results/emotion_with_memory_candidates_1"

    try:
        current_script_path = os.path.abspath(__file__)
    except NameError:
        current_script_path = os.getcwd()
        print(f"Warning: __file__ not defined. Using cwd: {current_script_path}")
    
    script_dir = os.path.dirname(current_script_path)
    absolute_output_folder = os.path.normpath(os.path.join(script_dir, relative_output_folder))
    output_file_path = os.path.join(absolute_output_folder, 'emotion_results.json')

    analyzer = EmotionAnalyzerWithMemory()
    analyzer.analyze_folder(input_folder_name)
    print(f"Attempting to save results to: {output_file_path}")
    analyzer.save_results(absolute_output_folder)
    print(f"Results should be saved in: {output_file_path}")
    if os.path.exists(output_file_path):
        print(f"Successfully saved results to {output_file_path}")
    else:
        print(f"Error: Results file was not created.")
    
if __name__ == "__main__":
    main()
