from random import randint


def fifo(access_num):
    if access_num in memory_of_process:
        return True
    else:
        memory_of_process.append(i)
        if len(memory_of_process) > num_each_process_memory:
            memory_of_process.pop(0)
        return False


def lru(access_num):
    if access_num in memory_of_process:
        memory_of_process.remove(access_num)
        memory_of_process.insert(0, access_num)
        return True
    else:
        memory_of_process.insert(0, access_num)
        if len(memory_of_process) > num_each_process_memory:
            memory_of_process.pop()
        return False


if_show_mode = True
repeat_num = 100
num_each_process_memory = 9
len_random_memory_access = 10
max_memory_num = 10
min_memory_num = 0
page_replacement_algorithms = {'fifo': fifo, 'lru': lru}
selected_algorithms = page_replacement_algorithms['fifo']

missing_count = 0
for repeat_i in range(1, repeat_num + 1):
    memory_of_process = list()
    memory_access_list = [randint(min_memory_num, max_memory_num) for i in range(len_random_memory_access)]
    if if_show_mode:
        print('第%d次测试，此次的随机访问序列是' % repeat_i, end='')
        print(memory_access_list)
    for i in memory_access_list:
        if if_show_mode:
            print('此次要访问的页面是%d' % i)
        if selected_algorithms(i):
            if if_show_mode:
                print('命中')
                input('回车继续\n')
        else:
            missing_count += 1
            if if_show_mode:
                print('未命中，访问后进程的内存为', end='')
                print(memory_of_process)
                input('回车继续\n')

print('缺页率%f' % (missing_count / (len_random_memory_access * repeat_num)))
