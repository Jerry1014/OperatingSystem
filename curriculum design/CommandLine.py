from os import system
from time import ctime

from Kernel import my_kernel, FileOrDirectoryToBig


class CommandLine:
    """
    用于用户交互的命令行界面
    """

    def __init__(self):
        self.user = CommandLine.login_in()
        # todo 当前工作目录初始化
        self._current_directory = '/'
        self.if_survival = True

    def parse_user_input(self, user_input):
        """
        处理用户输入
        """
        # 对命令进行切割
        command_list = user_input.split(' ')
        # todo 临时用于.和..路径的解析 以及 直接输入文件名应该对应当前工作目录
        for i in range(1, len(command_list)):
            if command_list[i][0] == '.':
                if command_list[i][1] == '.':
                    if len(self._current_directory) > 1:
                        command_list[i] = self._current_directory[:self._current_directory[:-1].rindex('/') + 1] + \
                                          command_list[i][3:]
                    else:
                        command_list[i] = '/'
                else:
                    command_list[i] = self._current_directory + command_list[i][2:]
        # 解析命令第一个参数
        if command_list[0] == 'ls':
            try:
                # 用户输入了路径参数 和 没有输入（当前路径）两种情况
                print(my_kernel.read_directory_or_file(
                    command_list[1] if len(command_list) > 1 else self._current_directory))
            except FileNotFoundError:
                print('路径错误')

        elif command_list[0] == 'df':
            item = my_kernel.show_disk_state()

            print('######################')
            print('卷名:', item[0])
            print('最后挂载时间:', ctime(item[1]))
            print('块大小:', item[2])
            print('inode 块大小:', item[3])
            print('总块数:', item[4])
            print('空闲块数:', item[5])
            print('总 inode 块数:', item[6])
            print('空闲 inode 块数:', item[7])
            print('######################')

        elif command_list[0] == 'mkdir':
            try:
                if command_list[1][-1] != '/':
                    raise AttributeError
                my_kernel.add_directory_or_file(command_list[1])
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出目录路径或路径不正确')

        elif command_list[0] == 'rm':
            try:
                my_kernel.remove_directory_or_file(command_list[1])
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出目录路径或路径不正确')

        elif command_list[0] == 'cat':
            try:
                if command_list[1][-1] == '/':
                    raise AttributeError
                tem = my_kernel.read_directory_or_file(command_list[1])
                print(tem)
            except FileNotFoundError:
                print('未给出文件路径或路径不正确')
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出文件路径或路径不正确')

        elif command_list[0] == 'creat':
            try:
                if command_list[1][-1] == '/':
                    raise AttributeError
                my_kernel.remove_directory_or_file(command_list[1])
                my_kernel.add_directory_or_file(command_list[1], command_list[2])
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出文件路径或路径不正确')

        elif command_list[0] == 'mv':
            try:
                if command_list[1][-1] == '/':
                    raise AttributeError
                tem_data = my_kernel.read_directory_or_file(command_list[1])
                my_kernel.remove_directory_or_file(command_list[1])
                my_kernel.add_directory_or_file(command_list[2], tem_data)
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出文件路径或路径不正确')

        elif command_list[0] == 'cp':
            try:
                if command_list[1][-1] == '/':
                    raise AttributeError
                tem_data = my_kernel.read_directory_or_file(command_list[1])
                my_kernel.add_directory_or_file(command_list[2], tem_data)
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出文件路径或路径不正确')

        elif command_list[0] == 'cd':
            try:
                if command_list[1][-1] != '/':
                    raise AttributeError
                my_kernel.read_directory_or_file(command_list[1])
                self._current_directory = command_list[1]
            except FileNotFoundError:
                print('未给出文件路径或路径不正确')
            except FileOrDirectoryToBig:
                print('文件或目录大小超出文件系统限制')
            except AttributeError:
                print('未给出文件路径或路径不正确')

        elif command_list[0] == 'pwd':
            print(self._current_directory)

        elif command_list[0] == 'link':
            try:
                my_kernel.add_hard_link(command_list[1],command_list[2])
            except AttributeError:
                print('参数错误')
        elif command_list[0] == 'exit':
            self.if_survival = False

        elif command_list[0] == 'mkfs':
            if self.user == 'root':
                my_kernel.format_hard_disk()
                self.if_survival = False
            else:
                print('权限不足')

        elif command_list[0] == 'useradd':
            try:
                if self.user == 'root':
                    user_name = command_list[1]
                    tem = my_kernel.read_directory_or_file('/etc/psw/psw.txt')
                    my_kernel.remove_directory_or_file('/etc/psw/psw.txt')
                    my_kernel.add_directory_or_file('/etc/psw/psw.txt', tem + ';%s;%s' % (user_name, ''))
                else:
                    print('请先通过sudo获取超级用户权限')
            except AttributeError:
                print('需指定用户名')

        elif command_list[0] == 'userdel':
            if len(command_list) < 2:
                print('需要输入用户的名字')
                return
            if self.user != 'root':
                print('请先通过sudo获取超级用户权限')
                return
            tem = my_kernel.read_directory_or_file('/etc/psw/psw.txt').split(';')
            user_psw = {tem[i]: tem[i + 1] for i in range(0, len(tem), 2)}
            if command_list[1] not in user_psw.keys():
                print('此用户不存在')
                return
            else:
                user_psw.pop(command_list[1])
                tem = list()
                for i, j in user_psw.items():
                    tem.append(i)
                    tem.append(j)
                my_kernel.remove_directory_or_file('/etc/psw/psw.txt')
                my_kernel.add_directory_or_file('/etc/psw/psw.txt', ';'.join(tem))

        elif command_list[0] == 'passwd':
            tem = my_kernel.read_directory_or_file('/etc/psw/psw.txt').split(';')
            user_psw = {tem[i]: tem[i + 1] for i in range(0, len(tem), 2)}

            if self.user == 'root' and len(command_list) > 1:
                user_will_change = command_list[1]
                if user_will_change not in user_psw.keys():
                    print('用户不存在')
                    return
            else:
                user_will_change = self.user
                old_psw = input('Old password:')
                if not old_psw == user_psw[self.user]:
                    print('密码错误')
                    return

            new_psw = input('New password:')
            if input('Pe-enter new password:') == new_psw:
                user_psw[user_will_change] = new_psw
                my_kernel.remove_directory_or_file('/etc/psw/psw.txt')
                tem = list()
                for i, j in user_psw.items():
                    tem.append(i)
                    tem.append(j)
                my_kernel.add_directory_or_file('/etc/psw/psw.txt', ';'.join(tem))
            else:
                print('两次输入的密码不一致')

    @staticmethod
    def login_in():
        """
        登录
        """
        try:
            tem = my_kernel.read_directory_or_file('/etc/psw/psw.txt').split(';')
            user_psw = {tem[i]: tem[i + 1] for i in range(0, len(tem), 2)}
        except FileNotFoundError:
            # 没有密码文件，即是第一次打开
            psw = input('你好，root用户，请输入密码\n')
            my_kernel.add_directory_or_file('/etc/psw/psw.txt', 'root;' + psw)
            return 'root'

        while True:
            user = input('账户\n')
            if user not in user_psw:
                print('用户不存在')
                continue
            if user_psw[user] == '':
                return user
            psw = input('密码\n')

            try:
                if user_psw[user] == psw:
                    system('cls')
                    return user
            except:
                print('账户或密码错误')


def get_user_input():
    system('cls')
    ui = CommandLine()
    start_of_line = ui.user + ':$ '
    if ui.user == 'root':
        start_of_line = ui.user + ':# '

    while ui.if_survival:
        user_input = input(start_of_line)
        ui.parse_user_input(user_input)

    system('cls')
