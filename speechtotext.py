from vosk import Model

english_model = Model(
    r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-en-us-0.15"
)

telugu_model = Model(
    r"C:\Users\avadh\OneDrive\Desktop\SpeechToText\models\vosk-model-small-te-0.42"
)

print("Both models loaded successfully!")
