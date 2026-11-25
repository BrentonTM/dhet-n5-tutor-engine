"""Validate an explicitly submitted Tex microphone recording."""

import base64
import binascii
import struct
from io import BytesIO
import wave

MAX_RECORDING_BYTES = 16000 * 2 * 60 + 44


def decode_voice_recording(event):
    """Return a bounded mono PCM WAV, or a safe error without echoing data."""
    error = "Tex could not read that recording. Please record the message again."
    if not isinstance(event, dict) or event.get("mime_type") != "audio/wav":
        return None, error
    identity = event.get("id")
    encoded = event.get("audio_base64")
    if (not isinstance(identity, str) or not 1 <= len(identity) <= 80
            or not isinstance(encoded, str) or not encoded
            or len(encoded) > ((MAX_RECORDING_BYTES + 2) // 3) * 4):
        return None, error
    try:
        audio = base64.b64decode(encoded, validate=True)
        if not 44 < len(audio) <= MAX_RECORDING_BYTES:
            return None, error
        with wave.open(BytesIO(audio), "rb") as clip:
            if (clip.getcomptype() != "NONE" or clip.getnchannels() != 1
                    or clip.getsampwidth() != 2 or clip.getframerate() != 16000
                    or not 0 < clip.getnframes() <= 16000 * 60):
                return None, error
            frames = clip.readframes(clip.getnframes())
            if len(frames) != clip.getnframes() * 2:
                return None, error
        if not any(frames):
            return None, "No sound was detected. Check the microphone in Tex's Settings and record again."
    except (ValueError, TypeError, binascii.Error, wave.Error, EOFError, struct.error):
        return None, error
    return audio, None
