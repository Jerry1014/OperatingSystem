class User:
    """
    用户类
    """

    def __init__(self):
        pass

    @staticmethod
    def login_in(user, psw):
        """
        登录
        """
        # todo 在这，会通过内核访问/etc/users文件，若无，则需要创建root账户
    # 我有计划将密码验证写到__new__里
