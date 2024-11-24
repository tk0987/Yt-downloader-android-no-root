from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import yt_dlp as youtube_dl
import os
from threading import Thread
import re
import logging


class MainApp(App):
    def build(self):
        root_layout = BoxLayout(orientation='vertical')

        # Background image
        background_image = Image(
            source='/storage/emulated/0/Music/muzyka/image000000.jpg',
            allow_stretch=True,
            keep_ratio=False,
            opacity=0.5,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Foreground layout
        content_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        scroll_view = ScrollView()
        inner_layout = BoxLayout(orientation='vertical', padding=[100, 100, 100, 100], spacing=40, size_hint_y=None)
        inner_layout.bind(minimum_height=inner_layout.setter('height'))

        link_label = Label(text='Paste YT link here:', font_size=80, color=(0, 0.5, 0.8, 1), size_hint_y=None, height=80)
        self.link_input = TextInput(hint_text='', font_size=50, multiline=False, halign="center", size_hint_y=None, height=150)

        dest_label = Label(text='Destination on device:', font_size=80, color=(0, 0.5, 0.8, 1), size_hint_y=None, height=80)
        self.dest_input = TextInput(
            text='/storage/emulated/0/Music/muzyka/',
            font_size=80,
            multiline=False,
            halign="center",
            size_hint_y=None,
            height=100
        )

        self.status_label = Label(text='', font_size=25, color=(0, 0.7, 0.2, 1), size_hint_y=None, height=15)
        download_button = Button(
            text="Download",
            font_size=80,
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=130
        )
        download_button.bind(on_release=self.on_download_button_click)

        inner_layout.add_widget(link_label)
        inner_layout.add_widget(self.link_input)
        inner_layout.add_widget(dest_label)
        inner_layout.add_widget(self.dest_input)
        inner_layout.add_widget(download_button)
        inner_layout.add_widget(Label(text='Download Info:', font_size=55, color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=65))
        inner_layout.add_widget(self.status_label)

        scroll_view.add_widget(inner_layout)
        content_layout.add_widget(scroll_view)
        root_layout.add_widget(background_image)
        root_layout.add_widget(content_layout)

        return root_layout

    def sanitize_filename(self, filename):
        return re.sub(r'[\\/:"*?<>|]+', '_', filename)

    def on_download_button_click(self, instance):
        url = self.link_input.text
        output_path = self.dest_input.text

        if not os.path.exists(output_path) or not os.path.isdir(output_path):
            self.update_status("Error: Directory does not exist.", (1, 0, 0, 1))
            return

        if not url:
            self.update_status("Error: Please enter a valid URL.", (1, 0, 0, 1))
            return

        self.update_status("Starting download...", (0, 0.5, 0.8, 1))
        Thread(target=self.download_and_convert_audio, args=(url, output_path)).start()

    def download_and_convert_audio(self, url, output_path):
        #os.system('chmod +x /storage/emulated/0/ffmpeg/bin/ffmpeg')
        #os.system('export LD_LIBRARY_PATH=$PREFIX/lib:/system/lib:/vendor/lib')
        ffmpeg_path= r'/storage/emulated/0/ffmpeg/bin/ffmpeg'
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        ydl_opts = { 
        'final_ext':'m4a',
        'format': 'bestaudio/best',
         'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'), 
         'ffmpeg_location': ffmpeg_path,
         'postprocessors': [{
         'key': 'FFmpegExtractAudio',
          'preferredcodec': 'm4a',
          }],
          
          'logger': logger
          }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                sanitized_title = self.sanitize_filename(info['title'])
                downloaded_file = os.path.join(output_path, f"{sanitized_title}.{info['ext']}")
                self.update_status("Downloaded", (0, 0.7, 0.2, 1))

              #  cd_file = os.path.join(output_path, f"{sanitized_title}.m4a")
                #self.convert_audio(str(downloaded_file), str(cd_file))
        except Exception as e:
            self.update_status(f"Done", (1, 0, 0, 1))

    def convert_audio(self, input_file, output_file):
        #command = f"/storage/emulated/0/ffmpeg/bin/ffmpeg -i \"{input_file}\" \"{output_file}\""
        print(f"Executing command: {command}")
        try:
            print("Before os.system")
            result = os.system(command)
            print(f"os.system result: {result}")
            if os.path.exists(output_file):
                self.update_status("Conversion complete", (0, 0.7, 0.2, 1))
            else:
                self.update_status("Conversion failed: Output file not found", (1, 0, 0, 1))
        except Exception as e:
            self.update_status(f"Error during conversion: {str(e)}", (1, 0, 0, 1))

    def update_status(self, message, color=(1, 1, 1, 1)):
        Clock.schedule_once(lambda dt: self._set_status(message, color), 0)

    def _set_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = color


if __name__ == '__main__':
    MainApp().run()
