class PermissionDenied(Exception):
    """
    权限不足异常
    注意，可通过PermissionDenied（msg）抛出具体的错误信息
    """


class InodeBlock:
    """
    inode节点类，具体的我还没想好
    """


class DataBlock:
    """
    data数据块类，具体的我还没想好
    """


class Kernel:
    """
    虚拟的内核，负责完成文件系统中的底层工作和虚拟硬盘的挂载，初始化等一系列操作
    """
    # 定义第一次/格式化硬盘时的超参数
    SIZE_OF_EACH_INODE_BLOCK = 10
    SIZE_OF_EACH_DATA_BLOCK = 10
    SUM_OF_INODE_BLOCK = 100
    SUM_OF_DATA_BLOCK = 100

    def __init__(self):
        # 以下变量均在挂载虚拟硬盘时初始化
        self._current_directory = None
        self._num_of_remaining_inode = None
        self._num_of_remaining_data_block = None
        self_size_of_each_inode_block = None
        self_size_of_each_data_block = None
        self._mount_hard_disk()

    @staticmethod
    def init_hard_disk():
        """
        建立虚拟硬盘文件并初始化
        切勿通过实例调用
        """

    def _mount_hard_disk(self):
        """实现虚拟硬盘的挂载和参数初始化"""
        # todo 检测虚拟硬盘文件是否存在，若否，则创建
        # todo 虚拟硬盘的初始化

    def _check_permission(self):
        """
        对操作进行权限检查
        """

    def add_directory(self):
        """
        添加目录文件
        """

    def read_directory(self):
        """
        读取目录文件
        """

    def remove_directory(self):
        """
        添加目录文件
        """

    def add_file(self):
        """
        添加文件
        """

    def read_file(self):
        """
        读取文件
        """

    def remove_file(self):
        """
        删除文件
        """

    def change_directory(self):
        """
        改变工作目录
        """


# 通过导入模块实现单例模式
# 在其他文件中通过 from kernel.py import kernel 导入单例
kernel = Kernel()
