import speech_recognition as sr
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import string
import os

# Configuration
BG_IMAGE_PATH = r"C:\Users\vivek\AudioToSignLanguageConverter-main\signlang1.jpg"
ISL_GIFS_PATH = r"C:\Users\vivek\AudioToSignLanguageConverter-main\TALK2SIGN\ISL_Gifs"
LETTERS_PATH = r"C:\Users\vivek\AudioToSignLanguageConverter-main\TALK2SIGN\letters"
STYLE_CONFIG = {
    "button_bg": "#2b2d42",      # Dark navy
    "text_color": "#2d2d2d",
    "hover_color": "#4a4e69",    # Deep slate
    "font": ("Helvetica", 12)

}

class GIFWindow(tk.Toplevel):
    """Window for displaying GIF animations"""
    def __init__(self, parent, gif_path):
        super().__init__(parent)
        self.title("Sign Language Animation")
        self.configure(bg='black')
        
        self.gif_label = ttk.Label(self)
        self.gif_label.pack(padx=20, pady=20)
        self.load_gif(gif_path)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy_cleanup)

    def load_gif(self, path):
        try:
            self.frames = []
            with Image.open(path) as im:
                try:
                    while True:
                        frame = ImageTk.PhotoImage(im.copy())
                        self.frames.append(frame)
                        im.seek(im.tell() + 1)
                except EOFError:
                    pass
                self.delay = im.info.get('duration', 100)
                self.animate(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {str(e)}")

    def animate(self, frame):
        if frame < len(self.frames):
            self.gif_label.config(image=self.frames[frame])
            self.after(self.delay, lambda: self.animate(frame + 1))

    def destroy_cleanup(self):
        self.frames = None
        self.destroy()

class SignLanguageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sign Language Converter")
        self.geometry("500x300")
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        
        # Setup background
        self.setup_background()
        self.setup_ui()
        self.load_phrases()
        
        self.bind('<Configure>', self.resize_background)

    def setup_background(self):
        try:
            self.bg_image = Image.open(BG_IMAGE_PATH)
            self.tk_bg_image = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = ttk.Label(self, image=self.tk_bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            self.configure(bg='#2d2d2d')

    def setup_ui(self):
        # Transparent main frame
        main_frame = ttk.Frame(self, style='Transparent.TFrame')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Control button
        self.control_btn = ttk.Button(
            main_frame,
            text="Start Listening",
            command=self.toggle_listening,
            style='Custom.TButton'
        )
        self.control_btn.pack(pady=20, ipadx=20, ipady=10)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Status: Ready",
            style='Status.TLabel'
        )
        self.status_label.pack(pady=10)

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Transparent.TFrame', background='')
        self.style.configure('Custom.TButton', 
                           background=STYLE_CONFIG['button_bg'],
                           foreground=STYLE_CONFIG['text_color'],
                           font=STYLE_CONFIG['font'])
        self.style.map('Custom.TButton',
                      background=[('active', STYLE_CONFIG['hover_color'])])
        self.style.configure('Status.TLabel',
                           background=STYLE_CONFIG['button_bg'],
                           foreground=STYLE_CONFIG['text_color'],
                           font=STYLE_CONFIG['font'])

    def load_phrases(self):
        self.phrases = [
            'hello', 'good morning', 'good night', 'thank you', 'please',
            'how are you', 'what is your name', 'where is the bathroom',
            'i need help', 'goodbye'
        ]

    def resize_background(self, event):
        try:
            resized = self.bg_image.resize((event.width, event.height))
            self.tk_bg_image = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.tk_bg_image)
        except AttributeError:
            pass

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.control_btn.config(text="Stop Listening")
        self.status_label.config(text="Status: Listening...")
        self.after(100, self.process_audio)

    def stop_listening(self):
        self.is_listening = False
        self.control_btn.config(text="Start Listening")
        self.status_label.config(text="Status: Ready")

    def process_audio(self):
        if self.is_listening:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    self.handle_input(text)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                self.after(100, self.process_audio)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.stop_listening()
            finally:
                if self.is_listening:
                    self.after(100, self.process_audio)

    def handle_input(self, text):
        clean_text = text.translate(str.maketrans('', '', string.punctuation))
        self.status_label.config(text=f"Heard: {clean_text}")

        if clean_text == 'goodbye':
            self.stop_listening()
            return

        gif_path = os.path.join(ISL_GIFS_PATH, f"{clean_text}.gif")
        if os.path.exists(gif_path):
            GIFWindow(self, gif_path)
        else:
            self.show_letters(clean_text)

    def show_letters(self, text):
        for char in text.lower():
            if char.isalpha():
                img_path = os.path.join(LETTERS_PATH, f"{char}.jpg")
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    plt.figure(figsize=(4, 4))
                    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    plt.axis('off')
                    plt.show(block=False)
                    plt.pause(1)
                    plt.close()

if __name__ == "__main__":
    app = SignLanguageApp()
    app.mainloop()