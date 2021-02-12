from tkinter import Tk, Frame
from tkinter import font as tkfont

from observer import Observer
from views.clock import ClockView
from views.voice import VoiceView
from views.dashboard import DashboardView



class ViewManager(Tk):
    settings = {
        "width": 320,
        "height": 480,
        "background": "black",
        "highlightthickness": 0,
    }
    current_frame = "ClockView"
    talk_view_interrupted = True

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.winfo_toplevel().title("bmw-assistant")
        self.config(cursor="none")
        self.overrideredirect(True)
        self.geometry(str(self.settings["width"]) + "x" + str(self.settings["height"]))
        self.title_font = tkfont.Font(
            family="Helvetica", size=18, weight="bold", slant="italic"
        )

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (VoiceView, DashboardView, ClockView):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ClockView")
        self.audio_observer = Observer(self.frames["VoiceView"].handleAudio)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_frame = page_name
        self.talk_view_interrupted = True

    def talk_start(self):
        frame = self.frames["VoiceView"]
        frame.tkraise()
        self.talk_view_interrupted = False

    def talk_stop(self):
        if not self.talk_view_interrupted:
            self.show_frame(self.current_frame)

    def queue_audio(self, buf):
        self.audio_observer.queue(buf)
