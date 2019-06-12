from States import *


class QueueIsEmpty(Exception):
    def __init__(self, msg):
        self.msg = msg


class AbstractDispatch:
    def __init__(self):
        pass


class Dispatch(AbstractDispatch):
    def __init__(self):
        super().__init__()
        self.new_state = FIFONewState()
        self.ready_state = FIFOReadyState()
        self.running_state = RunningState()
        self.block_state = BlockState()
        self.exit_state = ExitState()
        self.memory_left = 100
        self.pid_index = 0

    def add_new_state(self):
        need_memory = int(input('需要的内存空间\n'))
        self.new_state.add(Process(self.pid_index, need_memory))
        self.pid_index += 1

        # 触发从new到ready的调度
        if self.new_state.process_queue.qsize() == 1:
            self.dispatch_process_fr_ne_to_re()

    def dispatch_process_fr_ne_to_re(self):
        if not self.new_state.empty():
            tem = self.new_state.pop()
            if self.memory_left >= tem.need_memory:
                self.ready_state.add(tem)
                self.memory_left -= tem.need_memory

                # 触发从ready到running的调度
                if self.running_state.empty():
                    self.dispatch_process_fr_re_to_ru()
            else:
                self.new_state.add(tem)
                raise QueueIsEmpty('剩余内存不足')
        else:
            raise QueueIsEmpty('new_state为空')

    def dispatch_process_fr_re_to_ru(self):
        if not self.ready_state.empty():
            tem = self.running_state.pop()
            if tem:
                self.ready_state.add(tem)
            self.running_state.add(self.ready_state.pop())
        else:
            self.dispatch_process_fr_ne_to_re()

    def dispatch_process_fr_ru_to_re(self):
        if not self.running_state.empty():
            self.dispatch_process_fr_re_to_ru()
        else:
            raise QueueIsEmpty('running_state为空')

    def dispatch_process_fr_ru_to_bl(self):
        if not self.running_state.empty():
            self.block_state.add(self.running_state.pop())
            self.dispatch_process_fr_re_to_ru()
        else:
            raise QueueIsEmpty('running_state为空')

    def dispatch_process_fr_bl_to_re(self, pid):
        tem = self.block_state.remove(pid)
        if tem:
            self.ready_state.add(tem)
        else:
            raise QueueIsEmpty('block_state中无此进程')

    def dispatch_process_fr_ru_to_ex(self):
        if not self.running_state.empty():
            tem = self.running_state.pop()
            self.exit_state.add(tem)
            self.memory_left += tem.need_memory
            self.dispatch_process_fr_re_to_ru()
        else:
            raise QueueIsEmpty('running_state为空')

    def show(self):
        self.new_state.show()
        self.ready_state.show()
        self.running_state.show()
        self.block_state.show()
        self.exit_state.show()


singleton_dispatch = Dispatch()
