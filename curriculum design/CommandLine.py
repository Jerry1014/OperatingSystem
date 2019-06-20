from os import system

from Kernel import kernel


class CommandLine:
    """
    用于用户交互的命令行界面
    """

    def __init__(self):
        self.user = CommandLine.login_in()
        # todo 当前工作目录初始化
        self._current_directory = None

    def parse_user_input(self):
        """
        处理用户输入
        """

    @staticmethod
    def login_in():
        """
        登录
        """
        # todo 在这，会通过内核访问/etc/users文件，若无，则需要创建root账户
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
        print(user_input)

    # todo 当用户使用exit命令退出时，要考虑内核是否需要flush
