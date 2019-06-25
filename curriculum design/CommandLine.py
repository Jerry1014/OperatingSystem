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

    def parse_user_input(self, user_input):
        """
        处理用户输入
        """
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

    @staticmethod
    def login_in():
        """
        登录
        """
        # todo 在这，会通过内核访问/etc/users文件，若无，则需要创建root账户 暂且略过
        tem_login_test = {'root': "123456"}

        while True:
            user = input('账户\n')
            psw = input('密码\n')

            try:
                if tem_login_test[user] == psw:
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

    while True:
        user_input = input(start_of_line)
        ui.parse_user_input(user_input)

    # 当用户使用exit命令退出时，要考虑内核是否需要shutdown
