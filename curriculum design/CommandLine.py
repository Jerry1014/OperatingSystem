from os import system
from time import ctime

from Kernel import my_kernel, Msg


class CommandLine:
    """
    用于用户交互的命令行界面
    """

    def __init__(self):
        self.current_directory = '/'
        self.if_survival = True
        self.user = CommandLine.login_in()

    def parse_user_input(self, user_input):
        """
        处理用户输入
        """
        # 对命令进行切割
        command_list = user_input.split(' ')
        # todo 临时用于.和..路径的解析 以及 直接输入文件名应该对应当前工作目录 以及不给出路径时，应当未当前路径

        try:
            for i in range(1, len(command_list)):
                if command_list[i][0] == '.':
                    if command_list[i][1] == '.':
                        if len(self.current_directory) > 1:
                            command_list[i] = self.current_directory[:self.current_directory[:-1].rindex('/') + 1] + \
                                              command_list[i][3:]
                        else:
                            command_list[i] = '/'
                    else:
                        command_list[i] = self.current_directory + command_list[i][2:]

            # 解析命令第一个参数
            if command_list[0] == 'ls':
                # 用户输入了路径参数 和 没有输入（当前路径）两种情况
                if len(command_list) > 1 and command_list[1] == '-a':
                    file_directory_detail = [[i] + list(my_kernel.get_directory_file_info(self.current_directory + i,
                                                                                          my_kernel.all_user.index(
                                                                                              self.user)))
                                             for i in my_kernel.read_directory_or_file(
                            command_list[2] if len(command_list) > 2 else self.current_directory,
                            my_kernel.all_user.index(self.user))[2:]]
                    print('名字 类型 权限 大小 最后修改时间 所有者uid')
                    for i in file_directory_detail:
                        print('%s %s %s %i %s %i' % (
                            i[0], str(i[1], encoding='utf-8'), str(i[2], encoding='utf-8'), i[3], ctime(i[4]), i[5]))
                else:
                    print(my_kernel.read_directory_or_file(
                        command_list[1] if len(command_list) > 1 else self.current_directory,
                        my_kernel.all_user.index(self.user)))

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
                if command_list[1][-1] != '/':
                    raise AttributeError
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                my_kernel.add_directory_or_file(
                    command_list[1] if command_list[1][0] == '/' else self.current_directory + command_list[1],
                    my_kernel.all_user.index(self.user))

            elif command_list[0] == 'rm':
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                my_kernel.remove_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))

            elif command_list[0] == 'cat':
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                print(my_kernel.read_directory_or_file(command_list[1], my_kernel.all_user.index(self.user)))

            elif command_list[0] == 'creat':
                if command_list[1][-1] == '/':
                    raise AttributeError
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                my_kernel.remove_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))
                my_kernel.add_directory_or_file(command_list[1], my_kernel.all_user.index(self.user), command_list[2])

            elif command_list[0] == 'mv':
                if command_list[1][-1] == '/':
                    raise AttributeError
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                command_list[2] = command_list[2] if command_list[2][0] == '/' else self.current_directory + \
                                                                                    command_list[2]
                tem_data = my_kernel.read_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))
                my_kernel.remove_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))
                my_kernel.add_directory_or_file(command_list[2], my_kernel.all_user.index(self.user), tem_data)

            elif command_list[0] == 'cp':
                if command_list[1][-1] == '/':
                    raise AttributeError
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                command_list[2] = command_list[2] if command_list[2][0] == '/' else self.current_directory + \
                                                                                    command_list[2]
                tem_data = my_kernel.read_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))
                my_kernel.add_directory_or_file(command_list[2], my_kernel.all_user.index(self.user), tem_data)

            elif command_list[0] == 'cd':
                if command_list[1][-1] != '/':
                    raise AttributeError
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                my_kernel.read_directory_or_file(command_list[1], my_kernel.all_user.index(self.user))
                self.current_directory = command_list[1]

            elif command_list[0] == 'pwd':
                print(self.current_directory)

            elif command_list[0] == 'link':
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                command_list[2] = command_list[2] if command_list[2][0] == '/' else self.current_directory + \
                                                                                    command_list[2]
                my_kernel.add_hard_link(command_list[1], command_list[2], my_kernel.all_user.index(self.user))

            elif command_list[0] == 'chmod':
                command_list[1] = command_list[1] if command_list[1][0] == '/' else self.current_directory + \
                                                                                    command_list[1]
                if len(command_list[2]) != 3:
                    raise AttributeError
                else:
                    for i in command_list[2]:
                        if i != '0' and i != '1' and i != '3' and i != '4' and i != '5' and i != '6' and i != '8' and i != '9':
                            raise AttributeError
                my_kernel.change_mode(command_list[1], command_list[2], my_kernel.all_user.index(self.user))

            elif command_list[0] == 'exit':
                self.if_survival = False

            elif command_list[0] == 'mkfs':
                if self.user == 'root':
                    my_kernel.format_hard_disk()
                    self.if_survival = False
                else:
                    print('权限不足')

            elif command_list[0] == 'useradd':
                if self.user == 'root':
                    my_kernel.add_user(command_list[1])
                else:
                    print('请先通过sudo获取超级用户权限')

            elif command_list[0] == 'userdel':
                if self.user != 'root':
                    print('请先通过sudo获取超级用户权限')
                    return

                my_kernel.del_user(command_list[1])

            elif command_list[0] == 'passwd':
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
                            my_kernel.change_psw(self.user, new_psw)
                        else:
                            raise Msg('两次输入的密码不一致')

            elif command_list[0] == 'sudo':
                psw = input('password:')
                if psw != my_kernel.get_psw('root'):
                    raise Msg('密码错误')
                else:
                    self.user = 'root'
            else:
                raise Msg('无此命令')
        except Msg as e:
            print(e)
        except (IndexError, AttributeError):
            print('参数错误')

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

    while ui.if_survival:
        start_of_line = ui.user + ': ' + ui.current_directory + '$  '
        if ui.user == 'root':
            start_of_line = ui.user + ': ' + ui.current_directory + '#  '

        user_input = input(start_of_line)
        ui.parse_user_input(user_input)

    system('cls')
