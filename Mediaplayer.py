import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, filedialog

DESCRIPTION_FILE = 'descriptions.json'

class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Spotify-Style MP3 Player')
        self.geometry('550x500')
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

        # Player-Controls
        player_frame = tk.Frame(self, bg='#1a1a1a')
        player_frame.pack(pady=5, padx=10, fill=tk.X)
        self.play_button = tk.Button(player_frame, text='Play', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.play_song)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(player_frame, text='Stop', bg='#333', fg='white',
                                    activebackground='#1db954', command=self.stop_song)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Status-Anzeige
        status_frame = tk.Frame(self, bg='#1a1a1a')
        status_frame.pack(pady=5, padx=10, fill=tk.X)
        self.status_label = tk.Label(status_frame, text='Kein Song wird abgespielt',
                                    bg='#1a1a1a', fg='white')
        self.status_label.pack()

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

        self.current_song = None
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
            selected = self.listbox.curselection()
            if not selected:
                messagebox.showwarning('Warnung', 'Bitte wähle einen Song aus')
                return
            song = self.songs[selected[0]]
            self.current_song = song
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(self.music_folder, song))
            pygame.mixer.music.play()
            self.status_label.config(text=f'Jetzt läuft: {song}')
        except Exception as e:
            messagebox.showinfo('Info', 'Abspielen funktioniert nur lokal mit pygame und Audioausgabe')

    def stop_song(self):
        try:
            import pygame
            pygame.mixer.music.stop()
            self.status_label.config(text='Kein Song wird abgespielt')
            self.current_song = None
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