import tkinter as tk
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import threading

english_model = Model(r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-en-us-0.15")
telugu_model = Model(r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-te-0.42")

current_model = english_model

q = queue.Queue()

# ----------------------------
# Functions
# ----------------------------
def select_english():
    status_label.config(text="English Model Loaded", fg="green")

def select_telugu():
    status_label.config(text="Telugu Model Loaded", fg="green")

def start():
    caption.config(text="Listening...")

# ----------------------------
# Main Window
# ----------------------------
root = tk.Tk()
root.title("Live Speech To Text")
root.geometry("650x450")
root.resizable(False, False)

# ----------------------------
# Title
# ----------------------------
title = tk.Label(
    root,
    text="LIVE SPEECH TO TEXT",
    font=("Arial", 20, "bold")
)
title.pack(pady=20)

# ----------------------------
# Buttons
# ----------------------------
button_frame = tk.Frame(root)
button_frame.pack()

english_btn = tk.Button(
    button_frame,
    text="English",
    width=15,
    command=select_english
)
english_btn.grid(row=0, column=0, padx=10)

telugu_btn = tk.Button(
    button_frame,
    text="తెలుగు",
    width=15,
    command=select_telugu
)
telugu_btn.grid(row=0, column=1, padx=10)

# ----------------------------
# Status
# ----------------------------
status_label = tk.Label(
    root,
    text="English Model Loaded",
    fg="green",
    font=("Arial", 12, "bold")
)
status_label.pack(pady=15)

# ----------------------------
# Caption Area
# ----------------------------
caption = tk.Label(
    root,
    text="Waiting for speech...",
    bg="white",
    relief="solid",
    width=45,
    height=8,
    font=("Arial", 14)
)
caption.pack(pady=20)

# ----------------------------
# Start Button
# ----------------------------
start_btn = tk.Button(
    root,
    text="Start",
    width=15,
    bg="lightgreen",
    command=start
)
start_btn.pack()

root.mainloop()
