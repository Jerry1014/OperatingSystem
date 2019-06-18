from os import system

from Kernel import kernel
from Users import User


class CommandLine:
    """
    用于用户交互的命令行界面
    """

    def __init__(self):
        self.user = User()
        # todo 登录

    def parse_user_input(self):
        """
        处理用户输入
        """


def ui():
    system('cls')
    while True:
        user_input = input()
        print(user_input)
