from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json
import numpy as np

# ============================================================
# SETTINGS
# ============================================================

TELUGU_MODEL_PATH = r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-te-0.42"

# Change this if your microphone has a different device number
MICROPHONE_DEVICE = 1

# Vosk works best with 16 kHz mono PCM audio
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 4000

# ============================================================
# LOAD TELUGU MODEL
# ============================================================

print("Loading Telugu Vosk model...")
print("Model:", TELUGU_MODEL_PATH)
print()

try:
    model = Model(TELUGU_MODEL_PATH)
except Exception as error:
    print("ERROR: Could not load Telugu model")
    print(error)
    raise

recognizer = KaldiRecognizer(
    model,
    SAMPLE_RATE
)

print("Telugu model loaded successfully!")
print()

# ============================================================
# CHECK MICROPHONE
# ============================================================

print("Selected microphone:")
print(sd.query_devices(MICROPHONE_DEVICE))
print()

# ============================================================
# START MICROPHONE
# ============================================================

print("Starting microphone...")
print("Device:", MICROPHONE_DEVICE)
print("Sample rate:", SAMPLE_RATE)
print("Channels:", CHANNELS)
print()
print("Speak Telugu clearly.")
print()
print("Example:")
print("నా పేరు అవధ్")
print()
print("Press CTRL+C to stop.")
print()
print("====================================")
print("LISTENING FOR TELUGU...")
print("====================================")
print()

try:

    with sd.RawInputStream(
        device=MICROPHONE_DEVICE,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=CHANNELS
    ) as stream:

        while True:

            # Read raw 16-bit PCM audio directly
            data, overflowed = stream.read(BLOCK_SIZE)

            if overflowed:
                print("WARNING: Audio overflow")

            # ------------------------------------------------
            # Show microphone level
            # ------------------------------------------------

            audio = np.frombuffer(
                data,
                dtype=np.int16
            )

            if len(audio) > 0:

                level = np.max(
                    np.abs(audio)
                ) / 32768.0

                if level > 0.01:

                    print(
                        f"MIC: {level:.3f}",
                        end=" | ",
                        flush=True
                    )

            # ------------------------------------------------
            # Send directly to Vosk
            # ------------------------------------------------

            if recognizer.AcceptWaveform(data):

                result = json.loads(
                    recognizer.Result()
                )

                text = result.get(
                    "text",
                    ""
                ).strip()

                if text:

                    print()
                    print("TELUGU RESULT:")
                    print(text)
                    print()

            else:

                partial = json.loads(
                    recognizer.PartialResult()
                )

                partial_text = partial.get(
                    "partial",
                    ""
                ).strip()

                if partial_text:

                    print()
                    print("PARTIAL:")
                    print(partial_text)


except KeyboardInterrupt:

    print()
    print()
    print("====================================")
    print("TEST STOPPED")
    print("====================================")

    # Get anything remaining in Vosk's buffer
    final_result = json.loads(
        recognizer.FinalResult()
    )

    final_text = final_result.get(
        "text",
        ""
    ).strip()

    if final_text:
        print("FINAL:", final_text)


except Exception as error:

    print()
    print("====================================")
    print("ERROR")
    print("====================================")
    print(error)
