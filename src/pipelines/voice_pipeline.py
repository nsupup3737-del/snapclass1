import io
import numpy as np
import librosa
import streamlit as st


def get_voice_embedding(audio_bytes):
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        vec = np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1)])
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist() if norm > 0 else None
    except Exception:
        st.error("Voice recognition error")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.9):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sid, best_score = None, -1.0
    new_vec = np.array(new_embedding)
    for sid, stored in candidates_dict.items():
        if stored:
            score = float(np.dot(new_vec, np.array(stored)))
            if score > best_score:
                best_sid, best_score = sid, score

    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.9):
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)
        results = {}
        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            mfcc = librosa.feature.mfcc(y=audio[start:end], sr=sr, n_mfcc=20)
            vec = np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1)])
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue
            sid, score = identify_speaker((vec / norm).tolist(), candidates_dict, threshold)
            if sid and (sid not in results or score > results[sid]):
                results[sid] = score
        return results
    except Exception:
        st.error("Bulk process error")
        return {}
