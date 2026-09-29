import sounddevice as sd

MICROPHONE = 1

print("Selected microphone:")
print(sd.query_devices(MICROPHONE))

print("\nSpeak for 5 seconds...")

try:
    audio = sd.rec(
        int(5 * 16000),
        samplerate=16000,
        channels=1,
        dtype="int16",
        device=MICROPHONE
    )

    sd.wait()

    print("\nMicrophone test completed.")
    print("Maximum audio level:", abs(audio).max())

except Exception as e:
    print("\nERROR:")
    print(e)
