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

        self._cur_inode_tuple = None
        self._cur_inode_directory = None
        # todo 若实现了多线程下的多用户，则必须要考虑锁的问题

    def init_hard_disk(self):
        """
        建立虚拟硬盘文件并初始化
        """
        with open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'wb+') as f:
            # 超级块
            # todo 默认构建根路径后，可用节点和数据块数要更改
            f.write(
                struct.pack(Setting.SUPER_BLOCK_STRUCT, Setting.DEFAULT_DISK_NAME, time(),
                            Setting.SIZE_OF_EACH_DATA_BLOCK, Setting.SIZE_OF_EACH_INODE_BLOCK,
                            Setting.SUM_OF_DATA_BLOCK, Setting.SUM_OF_DATA_BLOCK - 1, Setting.SUM_OF_INODE_BLOCK,
                            Setting.SUM_OF_INODE_BLOCK - 1))

            # 块位图表
            for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
                f.write(struct.pack('I', 0b0))

            # 节点位图
            for i in range(Setting.SUM_OF_INODE_BLOCK // 32):
                f.write(struct.pack('I', 0b0))

            # 节点表 32B 填入全1是为了初始化之后，验证区块划分是否正确
            for i in range(Setting.SUM_OF_INODE_BLOCK):
                for j in range(8):
                    f.write(struct.pack('I', 0b11111111111111111111111111111111))

            # 块表 64B
            for i in range(Setting.SUM_OF_DATA_BLOCK):
                for i in range(16):
                    f.write(struct.pack('i', 0b0))

            # 创建根目录
            # todo 优化
            self._virtual_disk_file = f
            self._num_of_remaining_data_block = 1
            self._num_of_remaining_inode = 1
            inode_index = self._find__free_inode_block()
            data_block_index = self._find__free_data_block(1)[0]
            f.seek(Setting.START_OF_INODE_BLOCK)
            f.write(struct.pack(Setting.INODE_BLOCK_STRUCT, b'd', b'9', b'1', b'1', 0, time(), 0, data_block_index,
                                -1, -1, -1))
            f.seek(Setting.START_OF_DATA_BLOCK)
            f.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, 0, b'1' * Setting.MAX_LENGTH_OF_FILENAME, 0,
                                b'1' * Setting.MAX_LENGTH_OF_FILENAME, 0, b'1' * Setting.MAX_LENGTH_OF_FILENAME, 0))

            f.flush()

    def _mount_hard_disk(self):
        """实现虚拟硬盘的挂载和参数初始化"""
        if not path.exists(Setting.VIRTUAL_HARD_DISK_FILENAME):
            self.init_hard_disk()

        self._virtual_disk_file = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'rb+')
        super_block_bytes = self._virtual_disk_file.read(Setting.SIZE_OF_SUPER_BLOCK)
        self._disk_name, self._last_load_time, self._size_of_each_data_block, self._size_of_each_inode_block, \
        self._sum_of_data_block, self._num_of_remaining_data_block, self._sum_of_inode_block, \
        self._num_of_remaining_inode, *_ = struct.unpack(Setting.SUPER_BLOCK_STRUCT, super_block_bytes)

    def _find__free_inode_block(self):
        """
        查询第一个空的inode块序号，！！！此时若正确返回，则会修改相应的位图
        :return: 可用的inode序号，若无，则为None
        """
        if self._num_of_remaining_inode >= 1:
            self._num_of_remaining_inode -= 1
            self._virtual_disk_file.seek(Setting.START_OF_INODE_BLOCK_BITMAP)
            for i in range(Setting.SUM_OF_INODE_BLOCK // 32):
                a_32b_inode_block = format(struct.unpack('I', self._virtual_disk_file.read(4))[0], '032b')
                for j in range(len(a_32b_inode_block)):
                    if a_32b_inode_block[j] == '0':
                        self._virtual_disk_file.seek(-4, 1)
                        tem = int(a_32b_inode_block[:j] + '1' + a_32b_inode_block[j + 1:], 2)
                        self._virtual_disk_file.write(
                            struct.pack('I', tem))
                        return i * 32 + j
        return None

    def _find__free_data_block(self, n):
        """
        查询空的数据块序号
        :param n:需要的数据块数量
        :return: 可用的data块序号（元组），若无，则为None
        """
        if self._num_of_remaining_data_block >= n:
            result = list()
            self._virtual_disk_file.seek(Setting.START_OF_DATA_BLOCK_BITMAP)
            for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
                a_32b_data_block = format(struct.unpack('I', self._virtual_disk_file.read(4))[0], '032b')
                for j in range(len(a_32b_data_block)):
                    modify_record = list()
                    if a_32b_data_block[j] == '0':
                        result.append(i * 32 + j)
                        modify_record.append(j)

                        if len(result) == n:
                            a_32b_data_block = list(a_32b_data_block)
                            for k in modify_record:
                                a_32b_data_block[k] = '1'
                            a_32b_data_block = int(''.join(a_32b_data_block), 2)
                            self._virtual_disk_file.seek(-4, 1)
                            self._virtual_disk_file.write(struct.pack('I', a_32b_data_block))
                        return result
                    if len(modify_record) > 0:
                        a_32b_data_block = list(a_32b_data_block)
                        for k in modify_record:
                            a_32b_data_block[k] = '1'
                        a_32b_data_block = int(''.join(a_32b_data_block), 2)
                        self._virtual_disk_file.seek(-4, 1)
                        self._virtual_disk_file.write(struct.pack('I', a_32b_data_block))
        return None

    def _check_permission(self, uid, permission, owner, action):
        """
        对操作进行权限检查
        :param permission:文件中对权限的描述
        :param owner:文件中的拥有者信息
        :param action:对文件的操作
        :return:允许 True 拒绝 False
        """
        # root用户
        if uid == 0:
            return True
        # todo 对其他用户的权限检查

    def add_directory_or_file(self, directory, data=None):
        """
        添加目录或文件 默认递归创建
        :param directory: 要添加的完整路径 对于路径来说，形如/etc/psw/ !!!末尾的‘/’ 文件 /etc/psw/psw.txt
        :param data: 对于文件来说，这是文件的内容 目录无此参数 list 每一个item为一行
        :return:添加成功 True 添加失败 False 也可能抛出错误
        """
        new_inode = self._find__free_inode_block()
        if new_inode is not None:
            pass
        else:
            return False

    def remove_directory_or_file(self):
        """
        删除目录或文件
        """

    def read_directory(self):
        """
        读取目录文件
        """

    def read_file(self):
        """
        读取文件
        """

    def shut_down(self):
        self._virtual_disk_file.close()


# 通过导入模块实现单例模式
# 在其他文件中通过 from Kernel import kernel 导入单例
kernel = Kernel()
