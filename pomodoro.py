import tkinter as tk
import time
import threading
import random
import pygame  # audio

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 Pomodoro Timer 🌸")
        self.root.geometry("500x620")
        self.root.config(bg="#fff0f5")

        # Initialize audio
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.7)  # default volume

        # Default state
        self.focus_time = 25 * 60
        self.break_time = 5 * 60
        self.total_sessions = 4
        self.time_left = self.focus_time
        self.running = False
        self.is_break = False
        self.completed_sessions = 0

        # UI: Title
        tk.Label(
            root, text="Pomodoro Timer",
            font=("Comic Sans MS", 20, "bold"), bg="#fff0f5", fg="#ff69b4"
        ).pack(pady=10)

        # UI: Inputs (focus, break, sessions)
        input_frame = tk.Frame(root, bg="#fff0f5")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Focus (min):", bg="#fff0f5").grid(row=0, column=0, padx=5)
        self.focus_entry = tk.Entry(input_frame, width=5)
        self.focus_entry.insert(0, "25")
        self.focus_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Break (min):", bg="#fff0f5").grid(row=0, column=2, padx=5)
        self.break_entry = tk.Entry(input_frame, width=5)
        self.break_entry.insert(0, "5")
        self.break_entry.grid(row=0, column=3)

        tk.Label(input_frame, text="Sessions:", bg="#fff0f5").grid(row=0, column=4, padx=5)
        self.session_entry = tk.Entry(input_frame, width=5)
        self.session_entry.insert(0, "4")
        self.session_entry.grid(row=0, column=5)

        # UI: Timer display and status
        self.label = tk.Label(
            root, text="25:00", font=("Comic Sans MS", 40, "bold"),
            bg="#fff0f5", fg="#ff69b4"
        )
        self.label.pack(pady=20)

        self.status = tk.Label(
            root, text="Work Time 💻", font=("Arial", 14),
            bg="#fff0f5", fg="#9370db"
        )
        self.status.pack()

        # UI: Controls
        btn_frame = tk.Frame(root, bg="#fff0f5")
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(btn_frame, text="▶️ Start", command=self.start_timer,
                                   font=("Arial", 14), bg="#ffb6c1", width=8)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(btn_frame, text="⏸️ Pause", command=self.pause_timer,
                                   font=("Arial", 14), bg="#ffd700", width=8)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.continue_btn = tk.Button(btn_frame, text="▶️ Continue", command=self.continue_timer,
                                      font=("Arial", 14), bg="#90ee90", width=8)
        self.continue_btn.grid(row=0, column=2, padx=0)

        self.reset_btn = tk.Button(btn_frame, text="🔄 Reset", command=self.reset_timer,
                                   font=("Arial", 14), bg="#add8e6", width=8)
        self.reset_btn.grid(row=0, column=3, padx=5)

        # UI: Progress tracker
        self.progress_label = tk.Label(
            root, text=" Progress: ", font=("Arial", 14),
            bg="#fff0f5", fg="#ff69b4"
        )
        self.progress_label.pack(pady=10)

        # UI: Volume controls
        vol_frame = tk.Frame(root, bg="#fff0f5")
        vol_frame.pack(pady=10)

        tk.Label(vol_frame, text="🔊 Volume:", bg="#fff0f5").pack(side="left")
        self.vol_slider = tk.Scale(vol_frame, from_=0, to=100, orient="horizontal",
                                   command=self.set_volume, bg="#fff0f5")
        self.vol_slider.set(70)
        self.vol_slider.pack(side="left")

        self.mute_btn = tk.Button(vol_frame, text="Mute", command=self.mute_volume,
                                  font=("Arial", 10), bg="#ffb6c1")
        self.mute_btn.pack(side="left")

    # Audio helpers
    def play_sound(self, filename, loop=False):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"Audio file {filename} not found or failed to play: {e}")

    def stop_sound(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_volume(self, val):
        volume = max(0.0, min(1.0, float(val) / 100))
        pygame.mixer.music.set_volume(volume)

    def mute_volume(self):
        pygame.mixer.music.set_volume(0.0)
        self.vol_slider.set(0)

    # Controls
    def start_timer(self):
        if not self.running:
            try:
                self.focus_time = int(self.focus_entry.get()) * 60
                self.break_time = int(self.break_entry.get()) * 60
                self.total_sessions = int(self.session_entry.get())
            except ValueError:
                self.focus_time, self.break_time, self.total_sessions = 25 * 60, 5 * 60, 4

            self.time_left = self.focus_time
            self.running = True
            self.is_break = False

            # Audio: start beep then rain
            self.play_sound("beep.mp3", loop=False)
            threading.Timer(1.0, lambda: self.play_sound("rain.mp3", loop=True)).start()

            threading.Thread(target=self.countdown, daemon=True).start()

    def pause_timer(self):
        self.running = False
        # Keep ambient music as-is on pause (optional). To silence on pause, uncomment:
        # self.stop_sound()

    def continue_timer(self):
        if not self.running and self.time_left > 0:
            self.running = True
            threading.Thread(target=self.countdown, daemon=True).start()

    def reset_timer(self):
        self.running = False
        self.is_break = False
        self.time_left = self.focus_time
        self.label.config(text=f"{self.focus_time // 60:02d}:00", fg="#ff69b4")
        self.status.config(text="Work Time 💻", fg="#9370db")
        self.completed_sessions = 0
        self.update_progress()
        self.stop_sound()

    # Core loop
    def countdown(self):
        while self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.label.config(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            self.time_left -= 1

        if self.running:
            self.running = False
            self.confetti_animation()

            if not self.is_break:
                # Focus ended → alarm, then lofi for break
                self.play_sound("alarm.mp3", loop=False)
                threading.Timer(2.0, lambda: self.play_sound("lofi.mp3", loop=True)).start()

                self.completed_sessions += 1
                self.update_progress()

                self.status.config(text="Break Time ☕", fg="#32cd32")
                self.time_left = self.break_time
                self.is_break = True
                self.running = True
                threading.Thread(target=self.countdown, daemon=True).start()
            else:
                # Break ended → next focus or finish
                self.stop_sound()
                if self.completed_sessions < self.total_sessions:
                    self.status.config(text="Work Time 💻", fg="#9370db")
                    self.time_left = self.focus_time
                    self.is_break = False
                    self.running = True

                    self.play_sound("beep.mp3", loop=False)
                    threading.Timer(1.0, lambda: self.play_sound("rain.mp3", loop=True)).start()

                    threading.Thread(target=self.countdown, daemon=True).start()
                else:
                    # All sessions complete → celebratory chime
                    self.status.config(text="🎉 All sessions complete!", fg="#ff69b4")
                    self.play_sound("chime.mp3", loop=False)

    # Cute confetti
    def confetti_animation(self):
        confetti = tk.Canvas(self.root, width=400, height=150, bg="#fff0f5", highlightthickness=0)
        confetti.pack()
        colors = ["#ff69b4", "#9370db", "#add8e6", "#ffb6c1", "#32cd32"]
        for _ in range(50):
            x, y = random.randint(10, 390), random.randint(10, 140)
            confetti.create_oval(x, y, x + 8, y + 8, fill=random.choice(colors), outline="")
            self.root.update()
            time.sleep(0.03)
        confetti.destroy()

    # Progress hearts
    def update_progress(self):
        hearts = "❤️ " * self.completed_sessions
        self.progress_label.config(text=f" Progress: {hearts}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
