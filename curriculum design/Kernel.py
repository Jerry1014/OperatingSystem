import os
from math import ceil
from time import time

from Setting import Setting
from VirtualHardDiskDriver import VirtualHardDiskDriver


class Msg(Exception):
    """
    用于传送错误信息
    """


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
        self._virtual_hard_disk = VirtualHardDiskDriver()
        try:
            tem = self.read_directory_or_file('/etc/psw/psw.txt').split(';')
            self.user_psw = {tem[i]: tem[i + 1] for i in range(0, len(tem), 2)}
        except FileNotFoundError:
            self.user_psw = None

        # 若实现了多线程下的多用户，则必须要考虑锁的问题

    def _iterative_file_access(self, inode_index, target_file_directory_name, if_build_when_not_found, kind,
                               hard_link_inode=None):
        """
        迭代访问文件/目录  传入的inode应当为一个目录，否则报错
        :param inode_index: 在序号为index得inode节点寻找
        :param target_file_directory_name: 要寻找的下一文件/目录名
        :param if_build_when_not_found: 当无法找到需要的文件时，创建/抛出无文件错误标记
        :param kind: 要访问/创建的类型 f 文件 d 目录 h 硬链接
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

        # 需要创建相应的文件
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
                    new_data_block_index = self._virtual_hard_disk.find__free_data_block(1)[0]
                    inode_info[inode_info[2] + 4] = new_data_block_index
                    self._virtual_hard_disk.write_inode_block(inode_index, inode_info)

                    # 新建数据块
                    if kind == 'h':
                        new_inode_index_for_target = hard_link_inode
                    else:
                        new_inode_index_for_target = self._virtual_hard_disk.find__free_inode_block()
                    data_block_info = (
                        1, bytes(target_file_directory_name, encoding='utf-8'), new_inode_index_for_target,
                        b'1' * Setting.MAX_LENGTH_OF_FILENAME,
                        -1, b'1' * Setting.MAX_LENGTH_OF_FILENAME, -1)
                    self._virtual_hard_disk.write_data_block(new_data_block_index, data_block_info, True)

            else:
                # 修改当前数据块
                data_block_info = list(data_block_info)
                data_block_info[0] += 1
                data_block_info[data_block_info[0] * 2 - 1] = target_file_directory_name
                if kind == 'h':
                    new_inode_index_for_target = hard_link_inode
                else:
                    new_inode_index_for_target = self._virtual_hard_disk.find__free_inode_block()
                data_block_info[data_block_info[0] * 2] = new_inode_index_for_target
                self._virtual_hard_disk.write_data_block(data_block_pointer[inode_info[2] - 1], data_block_info, True)

            # 对于目录项，添加目录项的数据块
            if kind == 'd':
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

    def add_hard_link(self, directory, aim_directory):
        """
        创建一个硬链接（快捷方式）
        :param directory: 创建到目录
        :param aim_directory: 目标文件路径
        :return:
        """
        aim_inode = 0
        split_directory = aim_directory.split('/')
        aim_filename = split_directory[-1]
        for i in split_directory[1:]:
            aim_inode = self._iterative_file_access(aim_inode, i, False, 'f')

        next_index_of_inode = 0
        split_directory = directory.split('/')
        for i in split_directory[1:-1]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, True, 'd')
        self._iterative_file_access(next_index_of_inode, aim_filename, True, 'h', aim_inode)

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
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, True, 'd')

        # 创建的是文件
        if split_directory[-1] != '':
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, split_directory[-1], True, 'f')
            need_of_data_block = ceil(len(data) / Setting.SIZE_OF_EACH_DATA_BLOCK)
            if need_of_data_block == 0:
                need_of_data_block = 1
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

    def remove_directory_or_file(self, directory):
        """
        删除目录或文件
        :param directory: 要删除的完整路径
        """
        next_index_of_inode = 0
        split_directory = directory.split('/')
        if split_directory[-1] == '':
            split_directory.pop()

        # 迭代到上一节点处
        for i in split_directory[1:-1]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, False, 'd')

        # 修改上一节点的目录项，并取得删除节点的占用的块
        inode_info = list(self._virtual_hard_disk.read_inode_block(next_index_of_inode))
        data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
        for i in data_block_pointer[:inode_info[2]]:
            # 节点内文件指针遍历
            data_block_info = list(self._virtual_hard_disk.read_data_block(i, True))
            for j in range(data_block_info[0]):
                # 数据块目录项遍历
                if data_block_info[2 * j + 1] == split_directory[-1]:
                    # 删除节点占用的数据块
                    del_inode_info = self._virtual_hard_disk.read_inode_block(data_block_info[2 * j + 2])
                    del_data_block_pointer = del_inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
                    if del_inode_info[0] == 'f':
                        del_inode_info[2] = ceil(del_inode_info[2] / Setting.SIZE_OF_EACH_DATA_BLOCK)
                    for k in del_data_block_pointer[:del_inode_info[2]]:
                        self._virtual_hard_disk.remove_a_inode_or_a_data_block(k, False)
                    # 删除节点
                    self._virtual_hard_disk.remove_a_inode_or_a_data_block(data_block_info[2 * j + 2], True)
                    # 修改上一节点的目录项 todo 目录项的内碎片
                    data_block_info[0] -= 1
                    # the_last_data_block_info = self._virtual_hard_disk.read_data_block(
                    #     data_block_pointer[inode_info[2]-1], True)
                    # the_last_catalog_inode = the_last_data_block_info[the_last_data_block_info[0] * 2]
                    # the_last_catalog_filename = the_last_data_block_info[the_last_data_block_info[0] * 2 - 1]
                    # if the_last_data_block_info[0] == 1:
                    #     self._virtual_hard_disk.remove_a_inode_or_a_data_block(data_block_pointer[inode_info[2]-1], False)
                    #     inode_info[2] -= 1
                    # inode_info[inode_info[2] + 4] = -1
                    #
                    # data_block_info[2 * j + 1] = the_last_catalog_filename
                    # data_block_info[2 * j + 2] = the_last_catalog_inode
                    self._virtual_hard_disk.write_data_block(i, data_block_info, True)
                    self._virtual_hard_disk.write_inode_block(next_index_of_inode, inode_info)
                    return

    def read_directory_or_file(self, directory):
        """
        读取目录或文件
        :param directory: 要读取的目录/文件 完整路径
        :return :文件：str 文件内容 目录：list 目录下所有的目录/文件名
        """
        next_index_of_inode = 0
        split_directory = directory.split('/')
        for i in split_directory[1:-1]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, False, 'd')

        if split_directory[-1] != '':
            # 读取文件
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, split_directory[-1], False, 'f')
            inode_info = self._virtual_hard_disk.read_inode_block(next_index_of_inode)
            data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
            data = ''
            for i in data_block_pointer[:ceil(inode_info[2] / Setting.SIZE_OF_EACH_DATA_BLOCK)]:
                data += self._virtual_hard_disk.read_data_block(i, False)
            return data
        else:
            # 读取目录
            inode_info = self._virtual_hard_disk.read_inode_block(next_index_of_inode)
            data_block_pointer = inode_info[-Setting.NUM_POINTER_OF_EACH_INODE:]
            list_of_directory_and_file = list()
            for i in data_block_pointer[:inode_info[2]]:
                tem = self._virtual_hard_disk.read_data_block(i, True)
                list_of_directory_and_file += [tem[2 * i + 1] for i in range(tem[0])]
            return list_of_directory_and_file

    def get_directory_file_info(self, directory):
        """
        查看文件或目录的节点信息
        :param directory: 要读取的目录/文件 完整路径
        :return:
        """
        next_index_of_inode = 0
        split_directory = directory.split('/')
        if split_directory[-1] == '':
            split_directory.pop()
        for i in split_directory[1:]:
            next_index_of_inode = self._iterative_file_access(next_index_of_inode, i, False, 'd')

        return self._virtual_hard_disk.read_inode_block(next_index_of_inode)

    def show_disk_state(self):
        """
        返回当前硬盘状态 （超级块）
        :return: 虚拟硬盘文件的超级块
        """
        return self._virtual_hard_disk.show_disk_state()

    def format_hard_disk(self):
        self._virtual_hard_disk.format_hard_disk()
        # self._virtual_hard_disk.shut_down()
        # os.remove(Setting.VIRTUAL_HARD_DISK_FILENAME)
        # self._virtual_hard_disk = VirtualHardDiskDriver()

    def shut_down(self):
        # 保存密码文件到硬盘
        tem = list()
        for i, j in self.user_psw.items():
            tem.append(i)
            tem.append(j)
        try:
            self.remove_directory_or_file('/etc/psw/psw.txt')
        except FileNotFoundError:
            pass
        self.add_directory_or_file('/etc/psw/psw.txt', ';'.join(tem))

        self._virtual_hard_disk.shut_down()

    def add_user(self, username):
        # todo 未做用户数量限制，当超过最大文件大小时，会有bug发生
        if self.user_psw is None:
            self.user_psw = dict()
        self.user_psw[username] = ''

    def del_user(self, username):
        self.user_psw.pop(username)

    def change_psw(self, user, pwd):
        if user not in self.user_psw:
            raise Msg('无此用户')
        else:
            self.user_psw[user] = pwd

    def get_psw(self,username):
        if username not in self.user_psw:
            raise Msg('无此用户')
        else:
            return self.user_psw[username]


    # 通过导入模块实现单例模式


# 在其他文件中通过 from Kernel import my_kernel 导入单例
my_kernel = Kernel()
