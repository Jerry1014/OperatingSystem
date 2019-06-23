import struct
from math import ceil
from os.path import exists
from time import time

from Setting import Setting


class PermissionDenied(Exception):
    """
    权限不足异常
    注意，可通过PermissionDenied（msg）抛出具体的错误信息
    """


class NotADirectory(Exception):
    """
    传入非目录节点异常
    """


class FileOrDirectoryToBig(Exception):
    """
    本文件系统不支持的大文件或目录
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
            f.write(struct.pack(Setting.INODE_BLOCK_STRUCT, b'd', b'911', 1, time(), 0, data_block_index,
                                -1, -1, -1))
            f.seek(Setting.START_OF_DATA_BLOCK)
            f.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, 2, b'.', 0, b'..', 0,
                                b'1' * Setting.MAX_LENGTH_OF_FILENAME, -1))

            f.flush()

    def _mount_hard_disk(self):
        """实现虚拟硬盘的挂载和参数初始化"""
        if not exists(Setting.VIRTUAL_HARD_DISK_FILENAME):
            self.init_hard_disk()

        self._virtual_disk_file = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'rb+')
        super_block_bytes = self._virtual_disk_file.read(Setting.SIZE_OF_SUPER_BLOCK)
        self._disk_name, self._last_load_time, self._size_of_each_data_block, self._size_of_each_inode_block, \
        self._sum_of_data_block, self._num_of_remaining_data_block, self._sum_of_inode_block, \
        self._num_of_remaining_inode = struct.unpack(Setting.SUPER_BLOCK_STRUCT, super_block_bytes)

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

    def _iterative_file_access(self, inode_index, target_file_directory_name, if_build_when_not_found, if_file):
        """
        迭代访问文件/目录  传入的inode应当为一个目录，否则报错
        :param inode_index: 在序号为index得inode节点寻找
        :param target_file_directory_name: 要寻找的下一文件/目录名
        :param if_build_when_not_found: 当无法找到需要的文件时，创建/抛出无文件错误标记
        :param if_file: 要访问/创建的是否为文件
        :return: 目标文件的inode节点序号
        """
        if target_file_directory_name == '':
            return
        self._virtual_disk_file.seek(Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * inode_index)
        inode_info = struct.unpack(Setting.INODE_BLOCK_STRUCT,
                                   self._virtual_disk_file.read(Setting.SIZE_OF_EACH_INODE_BLOCK))

        if inode_info[0] == 'f':
            raise NotADirectory
        data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
        for i in data_block_pointer[:inode_info[2]]:
            # 节点内文件指针遍历
            self._virtual_disk_file.seek(Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * i)
            data_block_info = struct.unpack(Setting.DATA_BLOCK_DIRECTORY_STRUCT,
                                            self._virtual_disk_file.read(Setting.SIZE_OF_EACH_DATA_BLOCK))
            for j in range(data_block_info[0]):
                # 数据块目录项遍历
                filename = data_block_info[2 * j + 1][:data_block_info[2 * j + 1].index(b'\x00')].decode(
                    encoding='utf-8')
                if filename == target_file_directory_name:
                    return data_block_info[2 * j + 2]

        if if_build_when_not_found:
            # 添加新目录
            if data_block_info[0] == Setting.MAX_NUM_DIRECTORY:
                # 当前数据块已满
                if inode_info[2] >= Setting.NUM_POINTER_OF_EACH_INODE:
                    # 当前节点的数据块指针已用完
                    raise FileOrDirectoryToBig
                else:
                    # 修改节点
                    inode_info = list(inode_info)
                    inode_info[2] += 1
                    new_data_block_index = self._find__free_data_block(1)[0]
                    inode_info[inode_info[2] + 4] = new_data_block_index
                    self._virtual_disk_file.seek(
                        Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * inode_index)
                    self._virtual_disk_file.write(struct.pack(Setting.INODE_BLOCK_STRUCT, *inode_info))

                    # 新建数据块
                    new_inode_index_for_target = self._find__free_inode_block()
                    data_block_info = (
                        1, bytes(target_file_directory_name, encoding='utf-8'), new_inode_index_for_target,
                        b'1' * Setting.MAX_LENGTH_OF_FILENAME,
                        -1, b'1' * Setting.MAX_LENGTH_OF_FILENAME, -1)
                    self._virtual_disk_file.seek(
                        Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * new_data_block_index)
                    self._virtual_disk_file.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, *data_block_info))

            else:
                data_block_info = list(data_block_info)
                data_block_info[0] += 1
                data_block_info[data_block_info[0] * 2 - 1] = bytes(target_file_directory_name, encoding='utf-8')
                new_inode_index_for_target = self._find__free_inode_block()
                data_block_info[data_block_info[0] * 2] = new_inode_index_for_target
                self._virtual_disk_file.seek(
                    Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * data_block_pointer[
                        inode_info[2] - 1])
                self._virtual_disk_file.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, *data_block_info))

            if not if_file:
                new_data_block_index_for_target = self._find__free_data_block(1)[0]
                target_inode_info = (b'd', b'999', 1, time(), 0, new_data_block_index_for_target, -1, -1, -1)
                self._virtual_disk_file.seek(
                    Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * new_inode_index_for_target)
                self._virtual_disk_file.write(struct.pack(Setting.INODE_BLOCK_STRUCT, *target_inode_info))
                target_data_info = (
                    2, b'.', new_data_block_index_for_target, b'..', inode_index, b'1' * Setting.MAX_LENGTH_OF_FILENAME,
                    -1)
                self._virtual_disk_file.seek(
                    Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * new_data_block_index_for_target)
                self._virtual_disk_file.write(struct.pack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, *target_data_info))

            return new_inode_index_for_target
        else:
            raise FileNotFoundError

    def add_directory_or_file(self, directory, data=None):
        """
        添加目录或文件 默认递归创建
        :param directory: 要添加的完整路径 对于路径来说，形如/etc/psw/ !!!末尾的‘/’ 文件 /etc/psw/psw.txt
        :param data: 对于文件来说，这是文件的内容 目录无此参数 list 每一个item为一行 传入bytes
        :return:添加成功 True 添加失败 False 也可能抛出错误
        """
        next_index_of_inode = 0
        split_directory = directory.split('/')
        for i in split_directory[1:-1]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, True, False)

        # 创建的是文件
        if split_directory[-1] != '':
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, split_directory[-1], True, True)
            need_of_data_block = ceil(len(data) / Setting.SIZE_OF_EACH_DATA_BLOCK)
            if need_of_data_block > Setting.NUM_POINTER_OF_EACH_INODE:
                raise FileOrDirectoryToBig

            # 构建节点
            data_block_list = self._find__free_data_block(need_of_data_block)
            while len(data_block_list) < Setting.NUM_POINTER_OF_EACH_INODE:
                data_block_list.append(-1)
            inode_info = (b'f', b'999', len(data), time(), 0, *data_block_list)
            self._virtual_disk_file.seek(
                Setting.START_OF_INODE_BLOCK + Setting.SIZE_OF_EACH_INODE_BLOCK * next_index_of_inode)
            self._virtual_disk_file.write(struct.pack(Setting.INODE_BLOCK_STRUCT, *inode_info))

            # 构建数据块
            for i in range(need_of_data_block):
                self._virtual_disk_file.seek(
                    Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * data_block_list[i])
                self._virtual_disk_file.write(
                    data[Setting.SIZE_OF_EACH_DATA_BLOCK * i:Setting.SIZE_OF_EACH_DATA_BLOCK * (i + 1)])

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
        self._virtual_disk_file.seek(0)
        self._virtual_disk_file.write(struct.pack(Setting.SUPER_BLOCK_STRUCT, self._disk_name, time(),
                                                  self._size_of_each_data_block, self._size_of_each_inode_block,
                                                  self._sum_of_data_block, self._num_of_remaining_data_block,
                                                  self._sum_of_inode_block, self._num_of_remaining_inode))

        self._virtual_disk_file.close()


# 通过导入模块实现单例模式
# 在其他文件中通过 from Kernel import kernel 导入单例
kernel = Kernel()
