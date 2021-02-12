import audioop
from time import sleep
from tkinter import Frame, Canvas
from timeit import default_timer as timer

from audio_helpers import align_buf


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
            loudness = (
                audioop.max(align_buf(buf[chunk_size * i : chunk_size * (i + 1)], 2), 2)
                / 200.0
            )
            self.setLoudness(loudness)
            remaining = 0.05 / chunks - (timer() - start)
            if remaining > 0.001:
                sleep(remaining)
            start = timer()