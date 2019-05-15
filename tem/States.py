# -*- coding:utf-8 -*-
from queue import Queue


class Process:
    def __init__(self, pid):
        self.pid = pid

    def get_show_msg(self):
        return str(self.pid)


class AbstractState:
    def __init__(self):
        self.process_queue = list()

    def show(self):
        print(self.__class__.__name__ + '中的队列:', end=' ')
        if self.process_queue:
            for i in self.process_queue:
                print(i.get_show_msg(), end=', ')
            print()
        else:
            print('空')

    def empty(self):
        return len(self.process_queue) == 0


class AbstractNewState(AbstractState):
    def __init__(self):
        super().__init__()


class FIFONewState(AbstractNewState):
    def __init__(self):
        super().__init__()
        self.process_queue = Queue()

    def add(self, process):
        self.process_queue.put(process)

    def pop(self):
        return self.process_queue.get()

    def show(self):
        print(self.__class__.__name__ + '中的队列:', end=' ')
        if not self.process_queue.empty():
            for i in range(self.process_queue.qsize()):
                tem = self.process_queue.get()
                print(tem.get_show_msg(), end=', ')
                self.process_queue.put(tem)
            print()
        else:
            print('空')

    def empty(self):
        return self.process_queue.qsize() == 0


class AbstractReadyState(AbstractState):
    def __init__(self):
        super().__init__()


class FIFOReadyState(AbstractReadyState):
    def __init__(self):
        super().__init__()
        self.process_queue = Queue()

    def add(self, process):
        self.process_queue.put(process)

    def pop(self):
        return self.process_queue.get()

    def show(self):
        print(self.__class__.__name__ + '中的队列:', end=' ')
        if not self.process_queue.empty():
            for i in range(self.process_queue.qsize()):
                tem = self.process_queue.get()
                print(tem.get_show_msg(), end=', ')
                self.process_queue.put(tem)
            print()
        else:
            print('空')

    def empty(self):
        return self.process_queue.qsize() == 0


class AbstractRunningState(AbstractState):
    def __init__(self):
        super().__init__()


class RunningState(AbstractRunningState):
    def __init__(self):
        super().__init__()
        self.process_queue = None

    def add(self, process):
        self.process_queue = process

    def pop(self):
        tem, self.process_queue = self.process_queue, None
        return tem

    def empty(self):
        return self.process_queue is None

    def show(self):
        print(self.__class__.__name__ + '中的队列:', end=' ')
        if self.process_queue:
            print(self.process_queue.get_show_msg())
        else:
            print('空')


class AbstractBlockedState(AbstractState):
    def __init__(self):
        super().__init__()


class BlockState(AbstractBlockedState):
    def __init__(self):
        super().__init__()

    def add(self, process):
        self.process_queue.append(process)

    def remove(self, pid):
        for i in self.process_queue:
            if i.pid == pid:
                self.process_queue.remove(i)
                return i
        return None


class AbstractExitState(AbstractState):
    def __init__(self):
        super().__init__()


class ExitState(AbstractExitState):
    def __init__(self):
        super().__init__()

    def add(self, process):
        self.process_queue.append(process)
