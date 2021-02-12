from tkinter import Frame, Canvas, StringVar, Label

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