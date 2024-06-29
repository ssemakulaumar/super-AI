import pyttsx3
import speech_recognition as sr

class SpeechRecognitionModule:
    def __init__(self):
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.set_tts_properties()

        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def set_tts_properties(self, rate=150, volume=1.0, voice=None):
        # Set speaking rate
        self.tts_engine.setProperty('rate', rate)
        # Set volume level
        self.tts_engine.setProperty('volume', volume)
        # Set voice, if provided
        if voice:
            self.tts_engine.setProperty('voice', voice)

    def list_voices(self):
        voices = self.tts_engine.getProperty('voices')
        for idx, voice in enumerate(voices):
            print(f"Voice {idx + 1}: {voice.name} - {voice.id}")

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def recognize_speech(self):
        with self.microphone as source:
            self.speak("Listening for command...")
            print("Listening for command...")
            audio = self.recognizer.listen(source)

            try:
                print("Recognizing speech...")
                self.speak("Recognizing speech...")
                command = self.recognizer.recognize_google(audio).lower()
                print(f"Command received: {command}")
                return command
            except sr.UnknownValueError:
                self.speak("Sorry, I did not understand that.")
                print("Sorry, I did not understand that.")
                return None
            except sr.RequestError:
                self.speak("Could not request results; check your network connection.")
                print("Could not request results; check your network connection.")
                return None

    def process_voice_command(self, command):
        if command is None:
            return

        if "type" in command:
            text = command.replace("type", "").strip()
            self.speak(f"Typing: {text}")
            print(f"Typing: {text}")
            # Implement typing functionality here
        elif "move mouse to" in command:
            coords = command.replace("move mouse to", "").strip().split()
            if len(coords) == 2:
                x, y = int(coords[0]), int(coords[1])
                self.speak(f"Moving mouse to {x}, {y}")
                print(f"Moving mouse to {x}, {y}")
                # Implement mouse movement functionality here
        elif "click" in command:
            self.speak("Clicking mouse")
            print("Clicking mouse")
            # Implement mouse click functionality here
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            self.speak(f"Opening {app_name}")
            print(f"Opening {app_name}")
            # Implement application opening functionality here
        # Add more voice commands as needed

    def run(self):
        while True:
            command = self.recognize_speech()
            self.process_voice_command(command)

if __name__ == "__main__":
    srm = SpeechRecognitionModule()
    
    # List available voices
    print("Available voices:")
    srm.list_voices()

    # Set desired voice (optional)
    # srm.set_tts_properties(voice="HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0")

    # Start listening and processing voice commands
    srm.run()
