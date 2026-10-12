import os
import importlib.util

import dlib
import numpy as np
import streamlit as st
from sklearn.svm import SVC

from src.database.db import get_all_students


def _model_path(filename):
    """Locate a model file inside face_recognition_models without importing
    the package (its __init__.py needs pkg_resources)."""
    spec = importlib.util.find_spec("face_recognition_models")
    if spec is None or spec.origin is None:
        raise ImportError(
            "face_recognition_models is not installed. "
            "Run: pip install face_recognition_models"
        )
    path = os.path.join(os.path.dirname(spec.origin), "models", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return path


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        _model_path("shape_predictor_68_face_landmarks.dat")
    )

    facerec = dlib.face_recognition_model_v1(
        _model_path("dlib_face_recognition_resnet_model_v1.dat")
    )

    return detector, sp, facerec


def _to_rgb_uint8(image_np):
    """dlib needs an 8-bit RGB image. Drops the alpha channel if present."""
    image_np = np.asarray(image_np)
    if image_np.ndim == 3 and image_np.shape[2] == 4:
        image_np = image_np[:, :, :3]
    if image_np.dtype != np.uint8:
        image_np = image_np.astype(np.uint8)
    return np.ascontiguousarray(image_np)


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    image_np = _to_rgb_uint8(image_np)

    faces = detector(image_np, 1)
    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)  # 128-d embedding
        encodings.append(np.array(face_descriptor))

    return encodings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    # SVC needs at least 2 different students to train
    if len(set(y)) < 2:
        return {'clf': None, 'X': X, 'y': y}

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(X, y)
    except ValueError:
        clf = None

    return {'clf': clf, 'X': X, 'y': y}


def train_classifier():
    # Clear only the trained model cache, not the dlib/voice models
    get_trained_model.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    resemblance_threshold = 0.6

    for encoding in encodings:
        if clf is not None and len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]
        distance = np.linalg.norm(student_embedding - encoding)

        if distance <= resemblance_threshold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)