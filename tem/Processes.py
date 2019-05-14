class Process:
    def __init__(self, pid):
        self.pid = pid


class Processes:
    def __init__(self):
        self.process_list = list()
        self.index = 0

    def add(self):
        self.process_list.append(Process(self.index))
        self.index += 1

    def find(self, pid):
        for i in self.process_list:
            if i.pid == pid:
                return i
        return None

    def pop(self):
        self.process_list.pop()