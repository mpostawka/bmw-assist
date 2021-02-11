from tkinter import *
from tkinter import font as tkfont
import math
import audioop

from threading import Thread
from time import sleep
from datetime import datetime

from observer import Observer
from audio_helpers import align_buf

from timeit import default_timer as timer


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


class VoiceView(Frame):
    GRID_X = 3
    GRID_Y = 20
    LEFT_MARGIN = 40
    RIGHT_MARGIN = 55
    TOP_MARGIN = 60
    BOTTOM_MARGIN = 135
    PADDING_X = 20
    PADDING_Y = 3

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller.settings)
        self.controller = controller
        self.canvas = Canvas(self, controller.settings)
        self.canvas.pack()
        self.invocation_time = timer()
        true_size_x = (
            controller.settings["width"] - self.LEFT_MARGIN - self.RIGHT_MARGIN
        )
        true_size_y = (
            controller.settings["height"] - self.TOP_MARGIN - self.BOTTOM_MARGIN
        )
        cell_size_x = (true_size_x - (self.GRID_X - 1) * self.PADDING_X) / self.GRID_X
        cell_size_y = (true_size_y - (self.GRID_Y - 1) * self.PADDING_Y) / self.GRID_Y
        self.board = []
        for x in range(self.GRID_X):
            row = []
            for y in range(self.GRID_Y):
                cell_beginning_x = self.LEFT_MARGIN + x * (cell_size_x + self.PADDING_X)
                cell_beginning_y = self.TOP_MARGIN + y * (cell_size_y + self.PADDING_Y)
                row.append(
                    self.canvas.create_rectangle(
                        cell_beginning_x,
                        cell_beginning_y,
                        cell_beginning_x + cell_size_x,
                        cell_beginning_y + cell_size_y,
                        fill="#222200",
                    )
                )
            self.board.append(row)
        controller.update()

    def setColor(self, x, y, color):
        self.canvas.itemconfig(self.board[x][y], fill=color)
        self.controller.update()

    def setLoudness(self, loudness):
        self.invocation_time = timer()
        fill = loudness / 150.0
        for height in range(self.GRID_Y // 2):
            # middle bar
            if height / (self.GRID_Y / 2) < fill:
                self.setColor(1, 9 - height, "yellow")
                self.setColor(1, 10 + height, "yellow")
            else:
                self.setColor(1, 9 - height, "#222200")
                self.setColor(1, 10 + height, "#222200")
            # side bars
            decreased_height = min(height + 4, 9)
            if decreased_height / (self.GRID_Y / 2) < fill:
                self.setColor(0, 9 - height, "yellow")
                self.setColor(0, 10 + height, "yellow")
                self.setColor(2, 9 - height, "yellow")
                self.setColor(2, 10 + height, "yellow")
            else:
                self.setColor(0, 9 - height, "#222200")
                self.setColor(0, 10 + height, "#222200")
                self.setColor(2, 9 - height, "#222200")
                self.setColor(2, 10 + height, "#222200")

    def handleAudio(self, buf):
        start = timer()
        chunks = 1
        chunk_size = len(buf) // chunks
        for i in range(chunks):
            # can improve as below
            # ##############################################################
            # count = len(block) / 2
            # shorts = struct.unpack("%dh" % count, block)
            # sum_squares = sum(s**2 * SHORT_NORMALIZE**2 for s in shorts)
            # return Amplitude(math.sqrt(sum_squares / count))
            # ##############################################################
            loudness = (
                audioop.max(align_buf(buf[chunk_size * i : chunk_size * (i + 1)], 2), 2)
                / 200.0
            )
            self.setLoudness(loudness)
            remaining = 0.05 / chunks - (timer() - start)
            if remaining > 0.001:
                sleep(remaining)
            start = timer()


class DashboardView(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller.settings)
        self.controller = controller

        self.air = StringVar()
        self.engine = StringVar()
        self.battery = StringVar()
        air_label = Label(
            self,
            textvariable=self.air,
            fg="white",
            bg="black",
            font=controller.title_font,
        )
        engine_label = Label(
            self,
            textvariable=self.engine,
            fg="white",
            bg="black",
            font=controller.title_font,
        )
        battery_label = Label(
            self,
            textvariable=self.battery,
            fg="white",
            bg="black",
            font=controller.title_font,
        )

        air_label.place(x=60, y=100)
        engine_label.place(x=60, y=150)
        battery_label.place(x=60, y=200)

        self.setAir(0)
        self.setEngine(0)
        self.setBattery(0)

    def setAir(self, temp):
        self.air.set(f"Air: {temp:.1f}°C")

    def setEngine(self, temp):
        self.engine.set(f"Engine: {temp:.1f}°C")

    def setBattery(self, voltage):
        self.battery.set(f"Battery: {voltage:.1f}V")


class ClockView(Frame):
    LEFT_MARGIN = 0
    RIGHT_MARGIN = 20
    TOP_MARGIN = 20
    BOTTOM_MARGIN = 100
    HOUR_LENGTH = 0.55
    MINUTE_LENGTH = 0.86
    MINUTE_TAIL = 0.1

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller.settings)
        self.controller = controller
        self.canvas = Canvas(self, controller.settings)
        self.canvas.pack()

        self.size_x = (
            controller.settings["width"] - self.LEFT_MARGIN - self.RIGHT_MARGIN
        )
        self.size_y = (
            controller.settings["height"] - self.TOP_MARGIN - self.BOTTOM_MARGIN
        )
        self.center_x = self.LEFT_MARGIN + self.size_x / 2
        self.center_y = self.TOP_MARGIN + self.size_y / 2

        # draw hands
        self.hour_hand = self.canvas.create_line(
            self.center_x,
            self.center_y,
            self.center_x,
            self.center_y - (self.HOUR_LENGTH * self.size_y / 2),
            fill="white",
            width=7,
        )
        tail_length = self.MINUTE_TAIL * self.size_y / 2
        self.canvas.create_oval(
            self.center_x - tail_length - 3,
            self.center_y - tail_length - 3,
            self.center_x + tail_length + 3,
            self.center_y + tail_length + 3,
            fill="#101010",
        )
        self.minute_hand = self.canvas.create_line(
            self.center_x,
            self.center_y + tail_length,
            self.center_x,
            self.center_y - (self.MINUTE_LENGTH * self.size_y / 2),
            fill="white",
            width=7,
        )
        # draw reference
        for degrees in range(0, 360, 30):
            angle = math.radians(degrees)
            if degrees % 90 != 0:
                self.canvas.create_line(
                    math.sin(angle) * self.size_y / 3.7 + self.center_x,
                    math.cos(angle) * self.size_y / 3.7 + self.center_y,
                    math.sin(angle) * self.size_y / 2 + self.center_x,
                    math.cos(angle) * self.size_y / 2 + self.center_y,
                    fill="white",
                    width=5,
                )
        self.canvas.create_line(
            self.LEFT_MARGIN,
            self.TOP_MARGIN + self.size_y / 2,
            self.LEFT_MARGIN + self.size_x,
            self.TOP_MARGIN + self.size_y / 2,
            fill="white",
            width=3,
        )
        self.canvas.create_line(
            self.LEFT_MARGIN + self.size_x / 2,
            self.TOP_MARGIN,
            self.LEFT_MARGIN + self.size_x / 2,
            self.TOP_MARGIN + self.size_y,
            fill="white",
            width=3,
        )
        # draw plus minus
        position_x = 70
        position_y = 400
        distance_x = 100
        plus_width = 20
        plus_height = 20
        # self.canvas.create_line(position_x, position_y, position_x + plus_width, position_y, fill="white", width=3)
        # self.canvas.create_line(position_x + distance_x, position_y, position_x + distance_x + plus_width, position_y, fill="white", width=3)
        # self.canvas.create_line(position_x + distance_x + plus_width/2, position_y - plus_height/2, position_x + distance_x + plus_width/2, position_y + plus_height/2, fill="white", width=3)

    def setTime(self, time):
        minute_angle = math.radians((time.minute / 60.0) * 360.0)
        hour_angle = math.radians((time.hour / 12.0) * 360.0) + minute_angle / 12.0
        self.canvas.coords(
            self.minute_hand,
            -math.sin(minute_angle) * (self.MINUTE_TAIL * self.size_y / 2)
            + self.center_x,
            math.cos(minute_angle) * (self.MINUTE_TAIL * self.size_y / 2)
            + self.center_y,
            math.sin(minute_angle) * (self.MINUTE_LENGTH * self.size_y / 2)
            + self.center_x,
            -math.cos(minute_angle) * (self.MINUTE_LENGTH * self.size_y / 2)
            + self.center_y,
        )
        self.canvas.coords(
            self.hour_hand,
            self.center_x,
            self.center_y,
            math.sin(hour_angle) * (self.HOUR_LENGTH * self.size_y / 2) + self.center_x,
            -math.cos(hour_angle) * (self.HOUR_LENGTH * self.size_y / 2)
            + self.center_y,
        )


def foo(app):
    for i in range(20):
        sleep(2)
        app.frames["DashboardView"].setEngine(i)


def bar(app):
    for hour in range(24):
        for minute in range(60):
            sleep(0.1)
            app.frames["ClockView"].setTime(
                datetime.now().replace(hour=hour, minute=minute)
            )


def baz(app):
    for i in range(20):
        sleep(1.7)
        if i % 3 == 0:
            app.show_frame("DashboardView")
        elif i % 3 == 1:
            app.show_frame("VoiceView")
        else:
            app.show_frame("ClockView")


if __name__ == "__main__":
    app = ViewManager()
    for F in (foo, bar, baz):
        computer_thread = Thread(target=F, args=(app,))
        computer_thread.daemon = True
        computer_thread.start()
    app.mainloop()
