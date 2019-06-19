import os

from Dispatch import singleton_dispatch, QueueIsEmpty

while True:
    os.system('cls')
    singleton_dispatch.show()
    print('1.添加新进程')
    print('2.进程由new调度到ready')
    print('3.进程由ready调度到running')
    print('4.进程由running调度到ready')
    print('5.进程由running调度到block')
    print('6.进程由block调度到ready')
    print('7.进程由running调度到exit')

    choice = input()
    choices = {'1': singleton_dispatch.add_new_state,
               '2': singleton_dispatch.dispatch_process_fr_ne_to_re,
               '3': singleton_dispatch.dispatch_process_fr_re_to_ru,
               '4': singleton_dispatch.dispatch_process_fr_ru_to_re,
               '5': singleton_dispatch.dispatch_process_fr_ru_to_bl,
               '6': singleton_dispatch.dispatch_process_fr_bl_to_re,
               '7': singleton_dispatch.dispatch_process_fr_ru_to_ex}
    try:
        if choice == '6':
            block_process_pid = int(input('进程pid'))
            choices[choice](block_process_pid)
        else:
            choices[choice]()
    except KeyError:
        print('错误的输入')
    except QueueIsEmpty as e:
        print(e.msg)
