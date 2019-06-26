from os import system

from Kernel import my_kernel


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
        # todo useradd 添加用户
        # 对命令进行切割
        command_list = user_input.split(' ')
        # 解析命令第一个参数
        if command_list[0] == 'ls':
            try:
                # 用户输入了路径参数 和 没有输入（当前路径）两种情况
                print(my_kernel.read_directory_or_file(
                    command_list[1] if len(command_list) > 1 else self._current_directory))
            except FileNotFoundError:
                print('路径错误')

        elif command_list[0] == 'exit':
            self.if_survival = False

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
                tem2 = list()
                for i, j in user_psw.items():
                    tem2.append(i)
                    tem2.append(j)
                my_kernel.remove_directory_or_file('/etc/psw/psw.txt')
                try:
                    print(my_kernel.read_directory_or_file('/etc/psw/psw.txt'))
                except FileNotFoundError:
                    print('not found')
                my_kernel.add_directory_or_file('/etc/psw/psw.txt', ';'.join(tem2))
                print(my_kernel.read_directory_or_file('/etc/psw/psw.txt'))

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
