import struct
from os import path
from time import time

from Setting import Setting


class PermissionDenied(Exception):
    """
    权限不足异常
    注意，可通过PermissionDenied（msg）抛出具体的错误信息
    """


class InodeBlock:
    """
    inode节点类，解析节点内的数据
    """


class DataBlock:
    """
    data数据块类，具体的我还没想好
    """


class Kernel:
    """
    虚拟的内核，负责完成文件系统中的底层工作和虚拟硬盘的挂载，初始化等一系列操作
    """

    def __init__(self):
        # 以下变量均在挂载虚拟硬盘时初始化
        self._last_load_time = None
        self._num_of_remaining_inode = None
        self._num_of_remaining_data_block = None
        self._size_of_each_inode_block = None
        self._size_of_each_data_block = None
        self._sum_of_inode_block = None
        self._sum_of_data_block = None
        self._disk_name = None

        self._virtual_disk_file = None
        self._mount_hard_disk()
        # todo 若实现了多线程下的多用户，则必须要考虑锁的问题

    def init_hard_disk(self):
        """
        建立虚拟硬盘文件并初始化
        """
        self._virtual_disk_file = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'wb')
        # 超级块
        self._virtual_disk_file.write(
            struct.pack(Setting.SUPER_BLOCK_STRUCT, Setting.DEFAULT_DISK_NAME, time(),
                        Setting.SIZE_OF_EACH_DATA_BLOCK, Setting.SIZE_OF_EACH_INODE_BLOCK,
                        Setting.SUM_OF_DATA_BLOCK, Setting.SUM_OF_DATA_BLOCK, Setting.SUM_OF_INODE_BLOCK,
                        Setting.SUM_OF_INODE_BLOCK))

        # 块位图表
        for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
            self._virtual_disk_file.write(struct.pack('i', 0b00000000))

        # 节点位图
        for i in range(Setting.SUM_OF_INODE_BLOCK // 32):
            self._virtual_disk_file.write(struct.pack('i', 0b00000000))

        # 节点表 32B
        for i in range(Setting.SUM_OF_INODE_BLOCK):
            for j in range(8):
                self._virtual_disk_file.write(struct.pack('i', 0b0))

        # 块表 64B
        for i in range(Setting.SUM_OF_DATA_BLOCK):
            for i in range(16):
                self._virtual_disk_file.write(struct.pack('i', 0b0))

        # todo 写入根目录和/etc目录
        self._virtual_disk_file.flush()

    def _mount_hard_disk(self):
        """实现虚拟硬盘的挂载和参数初始化"""
        if not path.exists(Setting.VIRTUAL_HARD_DISK_FILENAME):
            self.init_hard_disk()

        if self._virtual_disk_file is None:
            self._virtual_disk_file = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'rb')
        super_block_bytes = self._virtual_disk_file.read(Setting.SIZE_OF_SUPER_BLOCK)
        self._disk_name, self._last_load_time, self._size_of_each_data_block, self._size_of_each_inode_block, \
        self._sum_of_data_block, self._num_of_remaining_data_block, self._sum_of_inode_block, \
        self._num_of_remaining_inode,*_ = struct.unpack(Setting.SUPER_BLOCK_STRUCT, super_block_bytes)

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

    def shut_down(self):
        self._virtual_disk_file.close()


# 通过导入模块实现单例模式
# 在其他文件中通过 from Kernel import kernel 导入单例
kernel = Kernel()
