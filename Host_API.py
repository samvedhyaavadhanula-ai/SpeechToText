import sounddevice as sd

print("HOST APIs")
print("================")

for i, api in enumerate(sd.query_hostapis()):
    print(i, "->", api["name"])

print("\nINPUT DEVICES")
print("================")

for i, device in enumerate(sd.query_devices()):
    if device["max_input_channels"] > 0:
        print(
            i,
            "->",
            device["name"],
            "| Host API:",
            device["hostapi"],
            "| Channels:",
            device["max_input_channels"],
            "| Rate:",
            device["default_samplerate"]
        )
