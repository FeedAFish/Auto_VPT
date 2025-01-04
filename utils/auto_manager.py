import threading
from utils import func


class AutoManager:
    def __init__(self):
        self.running = True
        self.event = threading.Event()
        self.autos = []

    def add_auto(self, title):
        auto = func.Auto_VPT(title)
        self.autos.append(auto)

    def loop(self):
        while self.running:
            try:
                for auto in self.autos:
                    if not auto.auto:
                        continue
                    auto.auto_toggle()
                # Use event instead of sleep for responsive shutdown
                self.event.wait(timeout=2)
            except Exception as e:
                print(f"Error in loop: {e}")
                self.stop()

    def stop(self):
        self.running = False
        self.event.set()
