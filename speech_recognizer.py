import speech_recognition as sr
import whisper
from datetime import datetime
import threading
import os

# Check available APIs
RECOGNITION_APIS = ["Google", "Sphinx", "Whisper"]  # You can add "Deepgram" if token available

# Supported Languages
LANGUAGE_OPTIONS = {
    "English": "en-US",
    "French": "fr-FR",
    "German": "de-DE",
    "Swahili": "sw-KE"
}

# Global control flags
is_paused = False
is_running = True

def transcribe_speech(api="Google", language="en-US"):
    global is_paused, is_running

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print(f"Listening... (API: {api}, Language: {language}) Press Ctrl+C to stop.")

        try:
            while is_running:
                if is_paused:
                    continue

                audio = r.listen(source, phrase_time_limit=5)

                try:
                    if api == "Google":
                        text = r.recognize_google(audio, language=language)
                    elif api == "Sphinx":
                        text = r.recognize_sphinx(audio, language=language)
                    elif api == "Whisper":
                        model = whisper.load_model("base")
                        audio_data = audio.get_wav_data()
                        with open("temp.wav", "wb") as f:
                            f.write(audio_data)
                        result = model.transcribe("temp.wav")
                        text = result['text']
                        os.remove("temp.wav")
                    else:
                        raise ValueError("Unsupported API selected.")

                    print("You said:", text)
                    save_to_file(text)

                except sr.UnknownValueError:
                    print("Could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results from {api} service; {str(e)}")

        except KeyboardInterrupt:
            print("\nRecognition stopped by user.")

def save_to_file(text):
    filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(text + "\n")
    print(f"Saved to {filename}")

def choose_api():
    print("Select Speech Recognition API:")
    for idx, name in enumerate(RECOGNITION_APIS, 1):
        print(f"{idx}. {name}")
    choice = int(input("Enter number: "))
    return RECOGNITION_APIS[choice - 1]

def choose_language():
    print("Select Language:")
    for idx, name in enumerate(LANGUAGE_OPTIONS.keys(), 1):
        print(f"{idx}. {name}")
    choice = int(input("Enter number: "))
    lang_name = list(LANGUAGE_OPTIONS.keys())[choice - 1]
    return LANGUAGE_OPTIONS[lang_name]

def control_listener():
    global is_paused, is_running
    while is_running:
        command = input("Enter command (pause/resume/exit): ").strip().lower()
        if command == "pause":
            is_paused = True
            print("Paused recognition.")
        elif command == "resume":
            is_paused = False
            print("Resumed recognition.")
        elif command == "exit":
            is_running = False
            print("Stopping app...")
            break

# Main
if __name__ == "__main__":
    api_choice = choose_api()
    lang_choice = choose_language()

    # Run the listener in a separate thread
    threading.Thread(target=control_listener, daemon=True).start()

    # Run speech recognition
    transcribe_speech(api=api_choice, language=lang_choice)
