class State:
    def __init__(self):
        self.queue = list()

    def add(self, process):
        self.queue.append(process)

    def pop(self):
        return self.queue.pop()


class NewState(State):
    def __init__(self):
        super().__init__()


class ReadyState(State):
    def __init__(self):
        super().__init__()


class RunningState(State):
    def __init__(self):
        super().__init__()


class BlockedState(State):
    def __init__(self):
        super().__init__()


class ExitState(State):
    def __init__(self):
        super().__init__()
