from math import ceil
from time import time

from Setting import Setting
from VirtualHardDiskDriver import virtual_hard_disk


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
        self._virtual_hard_disk = virtual_hard_disk
        # 若实现了多线程下的多用户，则必须要考虑锁的问题

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
        inode_info = self._virtual_hard_disk.read_inode_block(inode_index)

        if inode_info[0] == 'f':
            raise NotADirectory
        data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
        for i in data_block_pointer[:inode_info[2]]:
            # 节点内文件指针遍历
            data_block_info = self._virtual_hard_disk.read_data_block(i, True)
            for j in range(data_block_info[0]):
                # 数据块目录项遍历
                if data_block_info[2 * j + 1] == target_file_directory_name:
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
                    new_data_block_index = self._virtual_hard_disk.find__free_data_block()[0]
                    inode_info[inode_info[2] + 4] = new_data_block_index
                    self._virtual_hard_disk.write_inode_block(inode_index, inode_info)

                    # 新建数据块
                    new_inode_index_for_target = self._virtual_hard_disk.find__free_inode_block()
                    data_block_info = (
                        1, bytes(target_file_directory_name, encoding='utf-8'), new_inode_index_for_target,
                        b'1' * Setting.MAX_LENGTH_OF_FILENAME,
                        -1, b'1' * Setting.MAX_LENGTH_OF_FILENAME, -1)
                    self._virtual_hard_disk.write_data_block(new_data_block_index, data_block_info, True)

            else:
                data_block_info = list(data_block_info)
                data_block_info[0] += 1
                data_block_info[data_block_info[0] * 2 - 1] = target_file_directory_name
                new_inode_index_for_target = self._virtual_hard_disk.find__free_inode_block()
                data_block_info[data_block_info[0] * 2] = new_inode_index_for_target
                self._virtual_hard_disk.write_data_block(data_block_pointer[inode_info[2] - 1], data_block_info, True)

            if not if_file:
                new_data_block_index_for_target = self._virtual_hard_disk.find__free_data_block(1)[0]
                target_inode_info = (b'd', b'999', 1, time(), 0, new_data_block_index_for_target, -1, -1, -1)
                self._virtual_hard_disk.write_inode_block(new_inode_index_for_target, target_inode_info)
                target_data_info = (
                    2, b'.', new_data_block_index_for_target, b'..', inode_index, b'1' * Setting.MAX_LENGTH_OF_FILENAME,
                    -1)
                self._virtual_hard_disk.write_data_block(new_data_block_index_for_target, target_data_info, True)

            return new_inode_index_for_target
        else:
            raise FileNotFoundError

    def add_directory_or_file(self, directory, data=None):
        """
        添加目录或文件 默认递归创建
        :param directory: 要添加的完整路径 对于目录来说，形如/etc/psw/ !!!末尾的‘/’ 文件 /etc/psw/psw.txt
        :param data: 对于文件来说，这是文件的内容 目录无此参数 传入bytes
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
            data_block_list = self._virtual_hard_disk.find__free_data_block(need_of_data_block)
            while len(data_block_list) < Setting.NUM_POINTER_OF_EACH_INODE:
                data_block_list.append(-1)
            inode_info = (b'f', b'999', len(data), time(), 0, *data_block_list)
            self._virtual_hard_disk.write_inode_block(next_index_of_inode, inode_info)

            # 构建数据块
            if type(data) == 'str':
                data = bytes(data, encoding='utf-8')
            for i in range(need_of_data_block):
                self._virtual_hard_disk. \
                    write_data_block(data_block_list[i],
                                     data[Setting.SIZE_OF_EACH_DATA_BLOCK * i:Setting.SIZE_OF_EACH_DATA_BLOCK * (i + 1)]
                                     , False)

    def remove_directory_or_file(self):
        """
        删除目录或文件
        """

    def read_directory_or_file(self, directory):
        """
        读取目录或文件
        :param directory: 要读取的目录/文件 完整路径
        :return :文件：str 文件内容 目录：list 目录下所有的目录/文件名
        """
        next_index_of_inode = 0
        split_directory = directory.split('/')
        for i in split_directory[1:-1]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, False, False)

        if split_directory[-1] != '':
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, split_directory[-1], False, True)
            inode_info = self._virtual_hard_disk.read_inode_block(next_index_of_inode)
            data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
            data = ''
            for i in data_block_pointer[:inode_info[2]]:
                data += self._virtual_hard_disk.read_data_block(i, False)
            return data
        else:
            inode_info = self._virtual_hard_disk.read_inode_block(next_index_of_inode)
            data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
            list_of_directory_and_file = list()
            for i in data_block_pointer[:inode_info[2]]:
                tem = self._virtual_hard_disk.read_data_block(i, True)
                list_of_directory_and_file += [tem[2 * i + 1] for i in range(tem[0])]
            return list_of_directory_and_file

    def shut_down(self):
        self._virtual_hard_disk.shut_down()


# 通过导入模块实现单例模式
# 在其他文件中通过 from Kernel import kernel 导入单例
kernel = Kernel()
