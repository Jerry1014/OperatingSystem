from Settings import StateSettings


class State:
    def __init__(self, name):
        self.name = name


class StartState(State):
    def __init__(self, name):
        super().__init__(name)
