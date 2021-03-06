"""
虚拟硬盘的可视化工具
"""
import struct

from Setting import Setting


def visualization(filename_with_path):
    f = None
    try:
        f = open(filename_with_path, 'rb')
        while True:
            user_input = input('1.查看超级块\n'
                               '2.查看块位图\n'
                               '3.查看节点位图\n'
                               '4.查看节点表\n'
                               '5.查看块表\n'
                               '0.退出\n')
            if user_input == '0':
                break

            if user_input == '1':
                f.seek(0)
                print('卷名(char) 最后挂载时间(float) 块大小(int) inode块大小(int) 总块数(int) 空闲块数(int) 总inode块数(int) 空闲inode块数(int)')
                print(struct.unpack(Setting.SUPER_BLOCK_STRUCT, f.read(Setting.SIZE_OF_SUPER_BLOCK)))
            elif user_input == '2':
                f.seek(Setting.START_OF_DATA_BLOCK_BITMAP)
                for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
                    print(format(struct.unpack('I', f.read(4))[0], '032b'))
            elif user_input == '3':
                f.seek(Setting.START_OF_INODE_BLOCK_BITMAP)
                for i in range(Setting.SUM_OF_INODE_BLOCK // 32):
                    print(format(struct.unpack('I', f.read(4))[0], '032b'))
            elif user_input == '4':
                f.seek(Setting.START_OF_INODE_BLOCK)
                for i in range(Setting.SUM_OF_INODE_BLOCK):
                    print(struct.unpack(Setting.INODE_BLOCK_STRUCT, f.read(Setting.SIZE_OF_EACH_INODE_BLOCK)))
            elif user_input == '5':
                f.seek(Setting.START_OF_DATA_BLOCK)
                tem = f.read(Setting.SIZE_OF_EACH_DATA_BLOCK)
                count = 0
                print('第%d个节点' % count)
                print(tem)
                print('----------假装解析----------')
                print(struct.unpack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, tem))

                # todo 越界处理
                while True:
                    user_input_2 = input('n.下一页\n'
                                         '输入数字，跳转到该页\n'
                                         'q.退出\n')

                    if user_input_2 == 'q':
                        break
                    elif user_input_2 == 'n':
                        count += 1
                        print('第%d个1节点' % count)
                        tem = f.read(Setting.SIZE_OF_EACH_DATA_BLOCK)
                        print(tem)
                        print('----------假装解析----------')
                        print(struct.unpack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, tem))

                    elif user_input_2.isdigit():
                        count = int(user_input_2)
                        f.seek(Setting.START_OF_DATA_BLOCK + Setting.SIZE_OF_EACH_DATA_BLOCK * int(user_input_2))
                        tem = f.read(Setting.SIZE_OF_EACH_DATA_BLOCK)
                        print(tem)
                        print('----------假装解析----------')
                        print(struct.unpack(Setting.DATA_BLOCK_DIRECTORY_STRUCT, tem))

                    else:
                        print('错误的输入')

            else:
                print('错误的输入')
    except:
        pass
    finally:
        f.close() if f is not None else None


if __name__ == '__main__':
    visualization(Setting.VIRTUAL_HARD_DISK_FILENAME)
