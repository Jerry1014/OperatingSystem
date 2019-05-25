import os
import random


class MyQueue:
    def __init__(self):
        self.mylist = list()

    def add(self, item):
        self.mylist.insert(0, item)

    def pop(self):
        return self.mylist.pop()

    def size(self):
        return len(self.mylist)

    def show(self):
        return self.mylist


class Process:
    def __init__(self, pid):
        self.pid = pid

    def get_show_msg(self):
        return str(self.pid)


class Lock:
    def __init__(self, num):
        self.waiting_queue = MyQueue()
        self.num = num
        self.occupy_process = list()

    def P(self, process):
        if self.num < 1:
            print('进程' + process.get_show_msg() + '阻塞')
            self.waiting_queue.add(process)
        else:
            print('进程' + process.get_show_msg() + '进入')
            self.num -= 1
            process.step2()
            process.step3()


    def V(self):
            self.num += 1

            if self.waiting_queue.size() > 0:
                self.P(self.waiting_queue.pop())


L_empty = Lock(8)
L_filled = Lock(0)
list_of_free_producers = list()
list_of_free_customs = list()
buffer = list()


class a_producer(Process):
    def __init__(self, pid):
        super().__init__(pid)

    def step1(self):
        L_empty.P(self)

    def step2(self):
        print('进程' + str(self.pid) + '往缓冲放置了一个数据')
        buffer.append((self.pid, random.randint(0, 99)))

    def step3(self):
        L_filled.V()
        list_of_free_producers.append(self)



class a_custom(Process):
    def __init__(self, pid):
        super().__init__(pid)

    def step1(self):
        L_filled.P(self)

    def step2(self):
        print('进程' + str(self.pid) + '在缓冲取走了一个数据')
        buffer.pop()

    def step3(self):
        L_empty.V()
        list_of_free_customs.append(self)


pid = 0

while True:
    print('生产者队列',list_of_free_producers)
    print('消费者队列',list_of_free_customs)

    print('L_empty等待队列',L_empty.waiting_queue.show())
    print('L_filled等待队列',L_filled.waiting_queue.show())

    print('缓冲区',buffer)

    print('1.创建生产者进程')
    print('2.创建消费者进程')
    print('3.生产者生产')
    print('4.消费者消费')

    choice = int(input())
    if choice == 1:
        list_of_free_producers.append(a_producer(pid))
        pid += 1
    elif choice == 2:
        list_of_free_customs.append(a_custom(pid))
        pid += 1
    elif choice == 3:
        tem = list_of_free_producers.pop()
        tem.step1()
    elif choice == 4:
        tem = list_of_free_customs.pop()
        tem.step1()
