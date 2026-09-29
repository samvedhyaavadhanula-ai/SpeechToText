import tkinter as tk
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import numpy as np
import json
import threading
import os
import queue

# ============================================================
# SETTINGS
# ============================================================

ENGLISH_MODEL = r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-en-us-0.15"

TELUGU_MODEL = r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-te-0.42"

# Your confirmed working microphone
MIC_DEVICE = 1

# Microphone sample rate
MIC_RATE = 44100

# Vosk sample rate
VOSK_RATE = 16000

running = False

current_model = None
current_language = "English"

audio_queue = queue.Queue()


# ============================================================
# CHECK MODELS
# ============================================================

if not os.path.exists(ENGLISH_MODEL):
    print("English model not found:")
    print(ENGLISH_MODEL)
    raise SystemExit

if not os.path.exists(TELUGU_MODEL):
    print("Telugu model not found:")
    print(TELUGU_MODEL)
    raise SystemExit


# ============================================================
# LOAD MODELS
# ============================================================

print("Loading English model...")
english_model = Model(ENGLISH_MODEL)
print("English model loaded.")

print("Loading Telugu model...")
telugu_model = Model(TELUGU_MODEL)
print("Telugu model loaded.")

current_model = english_model

print("Both models loaded successfully!")


# ============================================================
# AUDIO CALLBACK
# ============================================================

def audio_callback(indata, frames, time, status):

    if status:
        print("Audio status:", status)

    audio_queue.put(bytes(indata))


# ============================================================
# CLEAR AUDIO QUEUE
# ============================================================

def clear_audio_queue():

    while not audio_queue.empty():

        try:
            audio_queue.get_nowait()

        except queue.Empty:
            break


# ============================================================
# RESAMPLE 44.1 kHz -> 16 kHz
# ============================================================

def resample_audio(audio):

    audio = np.asarray(audio).flatten()

    if len(audio) == 0:
        return np.array([], dtype=np.int16)

    new_length = int(
        len(audio) * VOSK_RATE / MIC_RATE
    )

    if new_length <= 0:
        return np.array([], dtype=np.int16)

    old_positions = np.linspace(
        0,
        len(audio) - 1,
        len(audio)
    )

    new_positions = np.linspace(
        0,
        len(audio) - 1,
        new_length
    )

    resampled = np.interp(
        new_positions,
        old_positions,
        audio
    )

    resampled = np.clip(
        resampled * 32767,
        -32768,
        32767
    ).astype(np.int16)

    return resampled


# ============================================================
# SAVE CAPTION
# ============================================================

def save_caption(text):

    with open(
        "captions.txt",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(text + "\n")


# ============================================================
# UPDATE CAPTION
# ============================================================

def show_caption(text):

    caption_label.config(
        text=text
    )


# ============================================================
# ENGLISH
# ============================================================

def select_english():

    global current_model
    global current_language

    if running:
        status_label.config(
            text="Stop first",
            fg="red"
        )
        return

    current_model = english_model
    current_language = "English"

    status_label.config(
        text="English Selected",
        fg="green"
    )

    caption_label.config(
        text="English selected. Press START."
    )


# ============================================================
# TELUGU
# ============================================================

def select_telugu():

    global current_model
    global current_language

    if running:
        status_label.config(
            text="Stop first",
            fg="red"
        )
        return

    current_model = telugu_model
    current_language = "Telugu"

    status_label.config(
        text="Telugu Selected",
        fg="green"
    )

    caption_label.config(
        text="Telugu selected. Press START."
    )


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def recognize_speech():

    global running

    recognizer = KaldiRecognizer(
        current_model,
        VOSK_RATE
    )

    print()
    print("====================================")
    print("STARTING SPEECH RECOGNITION")
    print("====================================")
    print("Language:", current_language)
    print("Microphone:", MIC_DEVICE)
    print("Microphone rate:", MIC_RATE)
    print("Vosk rate:", VOSK_RATE)
    print("====================================")
    print()

    try:

        # Use the same raw int16 approach that worked
        # in the Telugu-only test.

        with sd.RawInputStream(
            device=MIC_DEVICE,
            samplerate=MIC_RATE,
            blocksize=4410,
            dtype="int16",
            channels=1,
            callback=audio_callback
        ):

            print("LISTENING...")
            print("Speak now.")
            print()

            while running:

                data = audio_queue.get()

                if not data:
                    continue

                # Convert raw int16 bytes to numpy
                audio = np.frombuffer(
                    data,
                    dtype=np.int16
                ).astype(np.float32)

                # Convert int16 -> float
                audio = audio / 32768.0

                # Convert 44100 -> 16000
                audio_16k = resample_audio(audio)

                if len(audio_16k) == 0:
                    continue

                # Debug microphone level
                level = np.max(
                    np.abs(audio)
                )

                if level > 0.01:

                    print(
                        "MIC:",
                        round(float(level), 3),
                        end=" | "
                    )

                # Send converted audio to Vosk
                if recognizer.AcceptWaveform(
                    audio_16k.tobytes()
                ):

                    result = json.loads(
                        recognizer.Result()
                    )

                    text = result.get(
                        "text",
                        ""
                    ).strip()

                    if text:

                        print()
                        print("FINAL:")
                        print(text)
                        print()

                        root.after(
                            0,
                            show_caption,
                            text
                        )

                        save_caption(text)

                else:

                    partial_result = json.loads(
                        recognizer.PartialResult()
                    )

                    partial_text = partial_result.get(
                        "partial",
                        ""
                    ).strip()

                    if partial_text:

                        print()
                        print("PARTIAL:")
                        print(partial_text)

                        root.after(
                            0,
                            show_caption,
                            partial_text
                        )

    except Exception as error:

        print()
        print("====================================")
        print("MICROPHONE ERROR")
        print("====================================")
        print(error)
        print()

        root.after(
            0,
            lambda: status_label.config(
                text="Microphone Error",
                fg="red"
            )
        )


# ============================================================
# START
# ============================================================

def start():

    global running

    if running:
        return

    clear_audio_queue()

    running = True

    status_label.config(
        text="Listening... " + current_language,
        fg="blue"
    )

    caption_label.config(
        text="Listening..."
    )

    thread = threading.Thread(
        target=recognize_speech,
        daemon=True
    )

    thread.start()


# ============================================================
# STOP
# ============================================================

def stop():

    global running

    running = False

    clear_audio_queue()

    status_label.config(
        text="Stopped",
        fg="red"
    )

    caption_label.config(
        text="Waiting for speech..."
    )


# ============================================================
# CLOSE
# ============================================================

def close_app():

    global running

    running = False

    root.destroy()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Live Speech To Text Captioning"
)

root.geometry(
    "750x550"
)

root.resizable(
    False,
    False
)

root.protocol(
    "WM_DELETE_WINDOW",
    close_app
)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="LIVE SPEECH TO TEXT",
    font=("Arial", 22, "bold")
)

title.pack(
    pady=20
)


# ============================================================
# LANGUAGE BUTTONS
# ============================================================

language_frame = tk.Frame(root)

language_frame.pack()


english_button = tk.Button(
    language_frame,
    text="English",
    width=18,
    height=2,
    command=select_english
)

english_button.grid(
    row=0,
    column=0,
    padx=10
)


telugu_button = tk.Button(
    language_frame,
    text="తెలుగు",
    width=18,
    height=2,
    command=select_telugu
)

telugu_button.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="English Selected",
    fg="green",
    font=("Arial", 13, "bold")
)

status_label.pack(
    pady=15
)


# ============================================================
# CAPTION TITLE
# ============================================================

caption_title = tk.Label(
    root,
    text="LIVE CAPTION",
    font=("Arial", 14, "bold")
)

caption_title.pack()


# ============================================================
# CAPTION BOX
# ============================================================

caption_label = tk.Label(
    root,
    text="Waiting for speech...",
    bg="white",
    relief="solid",
    width=60,
    height=10,
    font=("Arial", 16),
    anchor="nw",
    justify="left",
    wraplength=680
)

caption_label.pack(
    pady=10
)


# ============================================================
# START / STOP
# ============================================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=15
)


start_button = tk.Button(
    button_frame,
    text="START",
    width=18,
    height=2,
    bg="lightgreen",
    command=start
)

start_button.grid(
    row=0,
    column=0,
    padx=10
)


stop_button = tk.Button(
    button_frame,
    text="STOP",
    width=18,
    height=2,
    bg="tomato",
    command=stop
)

stop_button.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# RUN
# ============================================================

root.mainloop()
