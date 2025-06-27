import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback

DESCRIPTION_FILE = 'descriptions.json'

class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yuri's MP3 Player")
        self.geometry('600x550')
        self.configure(bg='#1a1a1a')

        # Pfad zum aktuellen Verzeichnis (richtig für .py und .exe)
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        self.music_folder = os.path.join(current_dir, 'music')
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
        self.description_file = os.path.join(current_dir, DESCRIPTION_FILE)
        if not os.path.exists(self.description_file):
            with open(self.description_file, 'w') as f:
                json.dump({}, f)
        self.descriptions = self.load_descriptions()

        # Label für aktuellen Ordner
        self.folder_label = tk.Label(self, text=f"Aktueller Musikordner: {self.music_folder}",
                                    bg='#1a1a1a', fg='white', anchor='w', justify='left')
        self.folder_label.pack(pady=5, padx=10, fill=tk.X)

        # Song-Liste
        list_frame = tk.Frame(self, bg='#1a1a1a')
        list_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame, width=50, bg='#333', fg='white',
                                 selectbackground='#1db954', selectforeground='white')
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview,
                                bg='#333', troughcolor='#1a1a1a')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Status-Anzeige (Songname)
        status_frame = tk.Frame(self, bg='#1a1a1a')
        status_frame.pack(pady=5, padx=10, fill=tk.X)
        self.status_label = tk.Label(status_frame, text='Kein Song wird abgespielt',
                                    bg='#1a1a1a', fg='white')
        self.status_label.pack()

        # Player-Controls über der Fortschrittsleiste
        player_frame = tk.Frame(self, bg='#1a1a1a')
        player_frame.pack(pady=5, padx=10, fill=tk.X)
        self.prev_button = tk.Button(player_frame, text='Vorheriger', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.prev_song)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.play_button = tk.Button(player_frame, text='Play', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.play_song)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(player_frame, text='Stop', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.stop_song)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(player_frame, text='Nächster', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.next_song)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Grüne Fortschrittsleiste
        self.progress_frame = tk.Frame(self, bg='#1a1a1a')
        self.progress_frame.pack(pady=5, padx=10, fill=tk.X)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('green.Horizontal.TProgressbar', troughcolor='#333', background='#1db954')
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', length=400,
                                           mode='determinate', style='green.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, expand=True)

        # Zeit-Labels
        self.time_frame = tk.Frame(self, bg='#1a1a1a')
        self.time_frame.pack(pady=0, padx=10, fill=tk.X)
        self.current_time = tk.Label(self.time_frame, text='00:00', bg='#1a1a1a', fg='white')
        self.current_time.pack(side=tk.LEFT)
        self.total_time = tk.Label(self.time_frame, text='00:00', bg='#1a1a1a', fg='white')
        self.total_time.pack(side=tk.RIGHT)

        # Umbenennen
        rename_frame = tk.Frame(self, bg='#1a1a1a')
        rename_frame.pack(pady=5, padx=10, fill=tk.X)
        self.rename_label = tk.Label(rename_frame, text='Neuer Name:', bg='#1a1a1a', fg='white')
        self.rename_label.pack(side=tk.LEFT)
        self.rename_entry = tk.Entry(rename_frame, bg='#333', fg='white', insertbackground='white')
        self.rename_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.rename_button = tk.Button(rename_frame, text='Name ändern', bg='#333', fg='white',
                                      activebackground='#1db954', command=self.rename_song)
        self.rename_button.pack(side=tk.LEFT, padx=5)

        # Beschreibung
        desc_frame = tk.Frame(self, bg='#1a1a1a')
        desc_frame.pack(pady=5, padx=10, fill=tk.X)
        self.desc_label = tk.Label(desc_frame, text='Beschreibung:', bg='#1a1a1a', fg='white')
        self.desc_label.pack(side=tk.LEFT)
        self.desc_entry = tk.Entry(desc_frame, bg='#333', fg='white', insertbackground='white')
        self.desc_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.save_desc_button = tk.Button(desc_frame, text='Beschreibung speichern', bg='#333',
                                         fg='white', activebackground='#1db954', command=self.save_description)
        self.save_desc_button.pack(side=tk.LEFT, padx=5)

        # Ordner-Auswahl
        folder_frame = tk.Frame(self, bg='#1a1a1a')
        folder_frame.pack(pady=10, padx=10, fill=tk.X)
        self.folder_button = tk.Button(folder_frame, text='Ordner auswählen', bg='#333',
                                      fg='white', activebackground='#1db954', command=self.select_folder)
        self.folder_button.pack()

        self.current_song_index = None
        self.song_length = 0
        self.songs = []
        self.load_songs()
        self.listbox.bind('<<ListboxSelect>>', self.show_description)
        self.auto_refresh()

    def load_descriptions(self):
        with open(self.description_file, 'r') as f:
            return json.load(f)

    def save_descriptions(self):
        with open(self.description_file, 'w') as f:
            json.dump(self.descriptions, f)

    def auto_refresh(self):
        new_songs = [f for f in os.listdir(self.music_folder) if f.lower().endswith('.mp3')]
        if new_songs != self.songs:
            self.songs = new_songs
            self.listbox.delete(0, tk.END)
            for song in self.songs:
                self.listbox.insert(tk.END, song)
        self.after(2000, self.auto_refresh)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.music_folder = folder
            self.folder_label.config(text=f"Aktueller Musikordner: {self.music_folder}")
            self.load_songs()

    def load_songs(self):
        self.songs = [f for f in os.listdir(self.music_folder) if f.lower().endswith('.mp3')]
        self.listbox.delete(0, tk.END)
        for song in self.songs:
            self.listbox.insert(tk.END, song)

    def play_song(self):
        try:
            import pygame
            import mutagen.mp3
            selected = self.listbox.curselection()
            if not selected:
                messagebox.showwarning('Warnung', 'Bitte wähle einen Song aus')
                return
            self.current_song_index = selected[0]
            song = self.songs[self.current_song_index]
            song_path = os.path.join(self.music_folder, song)
            pygame.mixer.init()
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.status_label.config(text=f'Jetzt läuft: {song}')
            # Gesamtdauer des Songs ermitteln
            audio = mutagen.mp3.MP3(song_path)
            self.song_length = audio.info.length
            self.total_time.config(text=self.format_time(self.song_length))
            # Fortschrittsleiste zurücksetzen
            self.progress_bar['maximum'] = int(self.song_length)
            self.progress_bar['value'] = 0
            # Starte die Aktualisierung der Leiste
            self.update_progress()
            # Nach Song-Ende automatisch zum nächsten Song springen
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            self.bind(pygame.USEREVENT, self.next_song)
        except Exception as e:
            messagebox.showerror('Fehler', f'Fehler beim Abspielen:\n{e}\n\n{traceback.format_exc()}')

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_progress(self):
        try:
            import pygame
            if pygame.mixer.music.get_busy():
                current_pos = pygame.mixer.music.get_pos() / 1000  # ms in s umrechnen
                if current_pos < 0:  # pygame liefert manchmal -1
                    current_pos = 0
                self.progress_bar['value'] = current_pos
                self.current_time.config(text=self.format_time(current_pos))
            self.after(1000, self.update_progress)
        except:
            pass

    def next_song(self, event=None):
        try:
            import pygame
            if self.current_song_index is not None and self.songs:
                next_index = (self.current_song_index + 1) % len(self.songs)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_index)
                self.listbox.activate(next_index)
                self.current_song_index = next_index
                song = self.songs[next_index]
                song_path = os.path.join(self.music_folder, song)
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.status_label.config(text=f'Jetzt läuft: {song}')
                # Gesamtdauer des Songs ermitteln
                import mutagen.mp3
                audio = mutagen.mp3.MP3(song_path)
                self.song_length = audio.info.length
                self.total_time.config(text=self.format_time(self.song_length))
                self.progress_bar['maximum'] = int(self.song_length)
                self.progress_bar['value'] = 0
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
                self.bind(pygame.USEREVENT, self.next_song)
        except Exception as e:
            self.status_label.config(text='Fehler beim nächsten Song')

    def prev_song(self, event=None):
        try:
            import pygame
            if self.current_song_index is not None and self.songs:
                prev_index = (self.current_song_index - 1) % len(self.songs)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(prev_index)
                self.listbox.activate(prev_index)
                self.current_song_index = prev_index
                song = self.songs[prev_index]
                song_path = os.path.join(self.music_folder, song)
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.status_label.config(text=f'Jetzt läuft: {song}')
                # Gesamtdauer des Songs ermitteln
                import mutagen.mp3
                audio = mutagen.mp3.MP3(song_path)
                self.song_length = audio.info.length
                self.total_time.config(text=self.format_time(self.song_length))
                self.progress_bar['maximum'] = int(self.song_length)
                self.progress_bar['value'] = 0
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
                self.bind(pygame.USEREVENT, self.next_song)
        except Exception as e:
            self.status_label.config(text='Fehler beim vorherigen Song')

    def stop_song(self):
        try:
            import pygame
            pygame.mixer.music.stop()
            self.status_label.config(text='Kein Song wird abgespielt')
            self.current_song_index = None
            self.progress_bar['value'] = 0
            self.current_time.config(text='00:00')
        except:
            messagebox.showinfo('Info', 'Stop funktioniert nur lokal mit pygame')

    def rename_song(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning('Warnung', 'Bitte wähle einen Song aus')
            return
        new_name = self.rename_entry.get().strip()
        if not new_name.endswith('.mp3'):
            new_name += '.mp3'
        old_name = self.songs[selected[0]]
        old_path = os.path.join(self.music_folder, old_name)
        new_path = os.path.join(self.music_folder, new_name)
        if os.path.exists(new_path):
            messagebox.showerror('Fehler', 'Datei mit diesem Namen existiert bereits')
            return
        os.rename(old_path, new_path)
        if old_name in self.descriptions:
            self.descriptions[new_name] = self.descriptions.pop(old_name)
            self.save_descriptions()
        self.songs[selected[0]] = new_name
        self.load_songs()
        self.status_label.config(text=f'Umbenannt: {new_name}')

    def save_description(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning('Warnung', 'Bitte wähle einen Song aus')
            return
        song = self.songs[selected[0]]
        desc = self.desc_entry.get().strip()
        self.descriptions[song] = desc
        self.save_descriptions()
        messagebox.showinfo('Info', 'Beschreibung gespeichert')

    def show_description(self, event):
        selected = self.listbox.curselection()
        if not selected:
            return
        song = self.songs[selected[0]]
        desc = self.descriptions.get(song, '')
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, desc)

if __name__ == '__main__':
    app = MusicPlayer()
    app.mainloop()
