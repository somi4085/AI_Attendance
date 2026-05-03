from resemblyzer import VoiceEncoder, preprocess_wav
from silero_vad import load_silero_vad, get_speech_timestamps
import numpy as np
import io
import librosa
import streamlit as st


# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


@st.cache_resource
def load_vad_model():
    return load_silero_vad()


# ---------------- SINGLE VOICE EMBEDDING ----------------
def get_voice_embeddings(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        wav = preprocess_wav(audio)

        embedding = encoder.embed_utterance(wav)

        # ✅ FIXED JSON ISSUE
        return embedding.tolist()

    except Exception as e:
        st.error(f"Voice recog error: {e}")
        return None


# ---------------- IDENTIFY SPEAKER ----------------
def identify_speaker(
    new_embedding,
    candidate_dict,
    threshold=0.65
):
    if new_embedding is None or not candidate_dict:
        return None, 0.0

    # convert incoming list to numpy
    new_embedding = np.array(
        new_embedding,
        dtype=float
    )

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidate_dict.items():

        if stored_embedding is not None:

            stored_embedding = np.array(
                stored_embedding,
                dtype=float
            )

            similarity = np.dot(
                new_embedding,
                stored_embedding
            )

            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score


# ---------------- BULK AUDIO PROCESS ----------------
def process_bulk_audio(
    audio_bytes,
    candidate_dict,
    threshold=0.65
):
    try:
        encoder = load_voice_encoder()
        vad_model = load_vad_model()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        speech_timestamps = get_speech_timestamps(
            audio,
            vad_model
        )

        identified_result = {}

        for segment in speech_timestamps:

            start = segment["start"]
            end = segment["end"]

            segment_audio = audio[start:end]

            if len(segment_audio) < sr * 0.5:
                continue

            wav = preprocess_wav(segment_audio)

            embedding = encoder.embed_utterance(wav)

            sid, score = identify_speaker(
                embedding.tolist(),
                candidate_dict,
                threshold
            )

            if sid:
                if (
                    sid not in identified_result
                    or score > identified_result[sid]
                ):
                    identified_result[sid] = score

        return identified_result

    except Exception as e:
        st.error(f"Bulk process error: {e}")
        return {}