"""
虚拟硬盘的可视化工具
"""
import struct

from Setting import Setting

f = None
try:
    f = open(Setting.VIRTUAL_HARD_DISK_FILENAME, 'rb')
    while True:
        user_input = input('1.查看超级块\n'
                           '2.查看块位图\n'
                           '3.查看节点位图\n'
                           '4.查看节点表\n'
                           '5.查看块表\n'
                           '0.退出\n')
        if user_input == '0':
            break

        # todo 分页查看
        if user_input == '1':
            f.seek(0)
            print('卷名 最后挂载时间(char) 块大小(float) inode块大小(int) 总块数(int) 空闲块数(int) 总inode块数(int) 空闲inode块数(int)')
            print(struct.unpack(Setting.SUPER_BLOCK_STRUCT, f.read(Setting.SIZE_OF_SUPER_BLOCK)))
        elif user_input == '2':
            f.seek(Setting.SIZE_OF_SUPER_BLOCK)
            for i in range(Setting.SUM_OF_DATA_BLOCK // 32):
                print(format(struct.unpack('i', f.read(4))[0], '032b'))
        elif user_input == '3':
            f.seek(Setting.SIZE_OF_SUPER_BLOCK + Setting.SUM_OF_DATA_BLOCK // 32)
            for i in range(Setting.SUM_OF_INODE_BLOCK // 32):
                print(format(struct.unpack('i', f.read(4))[0], '032b'))
        elif user_input == '4':
            f.seek(Setting.SIZE_OF_SUPER_BLOCK + Setting.SUM_OF_DATA_BLOCK // 32 + Setting.SUM_OF_INODE_BLOCK // 32)
            for i in range(Setting.SUM_OF_INODE_BLOCK):
                print(struct.unpack(Setting.INODE_BLOCK_STRUCT, f.read(Setting.SIZE_OF_EACH_INODE_BLOCK)))
        elif user_input == '5':
            f.seek(
                Setting.SIZE_OF_SUPER_BLOCK + Setting.SUM_OF_DATA_BLOCK // 32 + Setting.SUM_OF_INODE_BLOCK // 32 +
                Setting.SUM_OF_INODE_BLOCK * Setting.SIZE_OF_EACH_INODE_BLOCK)
            for i in range(Setting.SUM_OF_DATA_BLOCK):
                # todo 根据数据块的类型解析？
                print(f.read(Setting.SIZE_OF_EACH_DATA_BLOCK))
        else:
            print('错误的输入')
except:
    pass
finally:
    f.close() if f is not None else None
