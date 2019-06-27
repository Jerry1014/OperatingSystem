import os
import struct
from os.path import exists
from time import time

from Setting import Setting


class VirtualHardDiskDriver:
    """
    虚拟硬盘文件的”驱动程序“，负责所有的虚拟硬盘文件的读写
    """

    def __init__(self):
        # 超级块变量
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

    def _init_hard_disk(self):
        """
        建立虚拟硬盘文件并初始化
        """
        with open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'wb+') as f:
            # 超级块
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

            f.flush()

            # 创建根目录
            # todo 优化
            self._virtual_disk_file = f
            self._num_of_remaining_data_block = 1
            self._num_of_remaining_inode = 1
            inode_index = self.find__free_inode_block()
            data_block_index = self.find__free_data_block(1)[0]
            f.seek(Setting.START_OF_INODE_BLOCK)
            f.write(struct.pack(Setting.INODE_BLOCK_STRUCT, b'd', b'999', 1, time(), 0, data_block_index,
                                -1, -1, -1))
            f.seek(Setting.START_OF_DATA_BLOCK)
            f.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, 2, b'.', 0, b'..', 0,
                                b'1' * Setting.MAX_LENGTH_OF_FILENAME, -1))

            f.flush()

    def _mount_hard_disk(self):
        """实现虚拟硬盘的挂载和参数初始化"""
        if not exists(Setting.VIRTUAL_HARD_DISK_FILENAME):
            self._init_hard_disk()

        self._virtual_disk_file = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'rb+')
        super_block_bytes = self._virtual_disk_file.read(Setting.SIZE_OF_SUPER_BLOCK)
        self._disk_name, self._last_load_time, self._size_of_each_data_block, self._size_of_each_inode_block, \
        self._sum_of_data_block, self._num_of_remaining_data_block, self._sum_of_inode_block, \
        self._num_of_remaining_inode = struct.unpack(Setting.SUPER_BLOCK_STRUCT, super_block_bytes)

    def find__free_inode_block(self):
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
                        self._virtual_disk_file.write(struct.pack('I', tem))
                        return i * 32 + j
        return None

    def remove_a_inode_or_a_data_block(self, index, if_inode):
        """
        删除一个节点，对节点位图进行修改
        :param index: 要删除的节点的序号
        :return: None
        """
        i = index // 32
        j = index % 32
        if if_inode:
            self._virtual_disk_file.seek(Setting.START_OF_INODE_BLOCK_BITMAP + i * 4)
        else:
            self._virtual_disk_file.seek(Setting.START_OF_DATA_BLOCK_BITMAP + i * 4)
        a_32b_block = format(struct.unpack('I', self._virtual_disk_file.read(4))[0], '032b')
        tem = int(a_32b_block[:j] + '0' + a_32b_block[j + 1:], 2)
        self._virtual_disk_file.seek(-4, 1)
        self._virtual_disk_file.write(struct.pack('I', tem))

    def find__free_data_block(self, n):
        """
        查询空的数据块序号
        :param n:需要的数据块数量
        :return: 可用的data块序号（列表），若无，则为None
        """
        if n <= 0:
            return AttributeError
        if self._num_of_remaining_data_block >= n:
            self._num_of_remaining_data_block -= n
            result = list()
            self._virtual_disk_file.seek(Setting.START_OF_DATA_BLOCK_BITMAP)
            for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
                a_32b_data_block = format(struct.unpack('I', self._virtual_disk_file.read(4))[0], '032b')
                modify_record = list()
                for j in range(len(a_32b_data_block)):
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

    def read_inode_block(self, index):
        """
        读取序号为index的节点内容
        :param index: 节点序号
        :return: tuple 具体内容可见于Setting.INODE_BLOCK_STRUCT
        """
        self._virtual_disk_file.seek(Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * index)
        return struct.unpack(Setting.INODE_BLOCK_STRUCT, self._virtual_disk_file.read(Setting.SIZE_OF_EACH_INODE_BLOCK))

    def write_inode_block(self, index, data):
        """
        将data写入序号为index的节点
        :param index: 节点序号
        :param data: list or tuple 写入的数据，结构为Setting.INODE_BLOCK_STRUCT
        :return: None
        """
        self._virtual_disk_file.seek(
            Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * index)
        self._virtual_disk_file.write(struct.pack(Setting.INODE_BLOCK_STRUCT, *data))

    def read_data_block(self, index, if_directory):
        """
        读取序号为index的数据块内容
        :param index: 数据块序号
        exit(0)

        :param if_directory: 目录块标记
        :return: 目录块：tuple 具体内容可见于Setting.DATA_BLOCK_DIRECTORY_STRUCT 文件：str 数据
        """
        self._virtual_disk_file.seek(Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * index)
        if if_directory:
            tem = list(struct.unpack(Setting.DATA_BLOCK_DIRECTORY_STRUCT,
                                     self._virtual_disk_file.read(Setting.SIZE_OF_EACH_DATA_BLOCK)))
            for j in range(tem[0]):
                tem[2 * j + 1] = tem[2 * j + 1][:tem[2 * j + 1].index(b'\x00')].decode(encoding='utf-8')
            return tuple(tem)
        else:
            tem = self._virtual_disk_file.read(Setting.SIZE_OF_EACH_DATA_BLOCK)
            try:
                return tem[:tem.index(b'\x00')].decode(encoding='utf-8')
            except ValueError:
                return tem.decode(encoding='utf-8')

    def write_data_block(self, index, data, if_directory):
        """
        将data写入序号为index的数据块
        :param index: 节点序号
        :param data: list or tuple 写入的数据，若是目录结构为Setting.DATA_BLOCK_DIRECTORY_STRUCT，文件则为要写入的bytes
        :param if_directory: 目录块标记
        :return: None
        """
        self._virtual_disk_file.seek(
            Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * index)
        if if_directory:
            data = list(data)
            for i in range(Setting.MAX_NUM_DIRECTORY):
                if type(data[2 * i + 1]) == str:
                    data[2 * i + 1] = bytes(data[2 * i + 1], encoding='utf-8')
            self._virtual_disk_file.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, *data))
        else:
            if type(data) == str:
                data = bytes(data, encoding='utf-8')
            if len(data) < Setting.SIZE_OF_EACH_DATA_BLOCK:
                data += b'\x00' * (Setting.SIZE_OF_EACH_DATA_BLOCK - len(data))
            self._virtual_disk_file.write(data)

    def show_disk_state(self):
        """
        返回当前硬盘状态 （超级块）
        :return: 虚拟硬盘文件的超级块
        """
        return (self._disk_name, self._last_load_time, self._size_of_each_data_block, self._size_of_each_inode_block,
                self._sum_of_data_block, self._num_of_remaining_data_block, self._sum_of_inode_block,
                self._num_of_remaining_inode)

    def shut_down(self):
        self._virtual_disk_file.seek(0)
        self._virtual_disk_file.write(struct.pack(Setting.SUPER_BLOCK_STRUCT, self._disk_name, time(),
                                                  self._size_of_each_data_block, self._size_of_each_inode_block,
                                                  self._sum_of_data_block, self._num_of_remaining_data_block,
                                                  self._sum_of_inode_block, self._num_of_remaining_inode))

        self._virtual_disk_file.close()

    def format_hard_disk(self):
        self.shut_down()
        os.remove(Setting.VIRTUAL_HARD_DISK_FILENAME)
        self._mount_hard_disk()
