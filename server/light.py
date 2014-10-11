import pingo


class Light:
    def __init__(self):
        board = pingo.detect.MyBoard()
        if board is None:
            board = pingo.ghost.GhostBoard()
            pin = board.pins[8]
        else:
            pin = board.pins[23]
        pin.mode = pingo.OUT
        self.pin = pin
        self.off()

    def __del__(self):
        self.off()

    def on(self):
        self.pin.hi()

    def off(self):
        self.pin.lo()

    def state(self):
        return self.pin.state is pingo.HIGH

    def set(self, on=True):
        if on:
            self.on()
        else:
            self.off()

    def toggle(self):
        self.set(not self.state())
