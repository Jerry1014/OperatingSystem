from os import system
from time import ctime

from Kernel import my_kernel, FileOrDirectoryToBig, Msg


class CommandLine:
    """
    用于用户交互的命令行界面
    """

    def __init__(self):
        self._current_directory = '/'
        self.if_survival = True
        self.user = CommandLine.login_in()

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
                if len(command_list) > 1 and command_list[1] == '-a':
                    file_directory_detail = [[i] + list(my_kernel.get_directory_file_info(self._current_directory + i))
                                             for i
                                             in my_kernel.read_directory_or_file(
                            command_list[2] if len(command_list) > 2 else self._current_directory)[2:]]
                    print('名字 类型 权限 大小 最后修改时间 所有者uid')
                    for i in file_directory_detail:
                        print('%s %s %s %i %s %i' % (
                            i[0], str(i[1], encoding='utf-8'), str(i[2], encoding='utf-8'), i[3], ctime(i[4]), i[5]))
                else:
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
                my_kernel.add_hard_link(command_list[1], command_list[2])
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
                    my_kernel.add_user(command_list[1])
                else:
                    print('请先通过sudo获取超级用户权限')
            except AttributeError:
                print('参数错误')

        elif command_list[0] == 'userdel':
            try:
                if self.user != 'root':
                    print('请先通过sudo获取超级用户权限')
                    return

                my_kernel.del_user(command_list[1])
            except Msg as e:
                print(e)
            except AttributeError:
                print('参数错误')

        elif command_list[0] == 'passwd':
            try:
                if self.user == 'root':
                    if len(command_list) == 1:
                        new_psw = input('New password:')
                        if input('Pe-enter new password:') == new_psw:
                            my_kernel.change_psw('root', new_psw)
                        else:
                            raise Msg('两次输入的密码不一致')
                    else:
                        new_psw = input('New password:')
                        if input('Pe-enter new password:') == new_psw:
                            my_kernel.change_psw(command_list[1], new_psw)
                else:
                    old_psw = input('Old password:')
                    if old_psw != my_kernel.get_psw(self.user):
                        raise Msg('密码错误')
                    else:
                        new_psw = input('New password:')
                        if input('Pe-enter new password:') == new_psw:
                            my_kernel.change_psw('root', new_psw)
                        else:
                            raise Msg('两次输入的密码不一致')
            except Msg as e:
                print(e)

    @staticmethod
    def login_in():
        """
        登录
        """
        if my_kernel.user_psw is None:
            psw = input('你好，root用户，请输入密码\n')
            my_kernel.add_user('root')
            my_kernel.change_psw('root', psw)
            return 'root'

        while True:
            user = input('账户\n')
            try:
                correct_psw = my_kernel.get_psw(user)
                if correct_psw == '':
                    return user
                psw = input('密码\n')

                if correct_psw == psw:
                    system('cls')
                    return user
                else:
                    print('密码错误')
            except Msg as e:
                print(e)


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
