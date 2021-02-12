import math
from tkinter import Frame, Canvas

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
        # position_x = 70
        # position_y = 400
        # distance_x = 100
        # plus_width = 20
        # plus_height = 20
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