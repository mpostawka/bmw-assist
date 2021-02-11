from time import sleep
from tkinter import Tk
from datetime import datetime
from timeit import default_timer as timer
from threading import Thread
from queue import Queue

from computer import Computer
from view_manager import ViewManager
import pushtotalk


def computer_process(view):
    dme = Computer()
    for i in range(100):
        sleep(1)
        try:
            status = dme.get_status()
            view.frames["DashboardView"].setAir(status["Air temperature"])
            view.frames["DashboardView"].setEngine(status["Engine temperature"])
            view.frames["DashboardView"].setBattery(status["Battery voltage"])
        except:
            pass


def assistant_process(view):
    pushtotalk.main(view=view)


def clock_process(view):
    while True:
        sleep(1)
        # update timer
        view.frames["ClockView"].setTime(datetime.now())
        # clear voice view if unused
        if timer() - view.frames["VoiceView"].invocation_time > 1:
            view.frames["VoiceView"].setLoudness(0)


def main():
    view = ViewManager()
    view.show_frame("ClockView")
    clock_thread = Thread(target=clock_process, args=(view,), daemon=True)
    clock_thread.start()
    computer_thread = Thread(target=computer_process, args=(view,), daemon=True)
    computer_thread.start()
    assistant_thread = Thread(target=assistant_process, args=(view,), daemon=True)
    assistant_thread.start()
    view.mainloop()


if __name__ == "__main__":
    main()
