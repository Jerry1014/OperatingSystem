class Setting:
    # 注意！写入文件的char类型，传值必须是len=1 的bytes
    DEFAULT_DISK_NAME = b'C'
    VIRTUAL_HARD_DISK_FILENAME = 'my_virtual_hard_disk'
    # struct定义
    # 超级块
    # 卷名 最后挂载时间(char) 块大小(float) inode块大小(int) 总块数(int) 空闲块数(int) 总inode块数(int) 空闲inode块数(int)
    # 节点块
    # 类型(char) 权限(char*3 所有者/群组/其他) 大小(int) 最后修改时间(float) 所有者uid(int) 直接指针(int*16)
    # 数据块 - 目录
    # 目录下的文件数 (文件名(char*16) inode节点(int)) * 3
    SUPER_BLOCK_STRUCT = 'cf6i'
    INODE_BLOCK_STRUCT = 'c3cifi4i'
    DATA_BLOCK_DIRECTORY_STRUCT = 'i' + 3 * '16ci'

    # 注意！此处虽然超级块只占用了29B，但在读写写入时都会有对齐操作，所以读取时应当读取32B
    SIZE_OF_SUPER_BLOCK = 32
    SIZE_OF_EACH_INODE_BLOCK = 32
    SIZE_OF_EACH_DATA_BLOCK = 64

    # 为了方便块位图的存储，块数节点数均要乘8
    SUM_OF_INODE_BLOCK = 1 * 32
    SUM_OF_DATA_BLOCK = 10 * 32
    # 文件名最大长度 单位char
    MAX_LENGTH_OF_FILENAME = 12

    # 各个区块起始偏移量计算
    START_OF_DATA_BLOCK_BITMAP = SIZE_OF_SUPER_BLOCK
    START_OF_INODE_BLOCK_BITMAP = SIZE_OF_SUPER_BLOCK + SUM_OF_DATA_BLOCK // 8
    START_OF_INODE_BLOCK = SIZE_OF_SUPER_BLOCK + SUM_OF_DATA_BLOCK // 8 + SUM_OF_INODE_BLOCK // 8
    START_OF_DATA_BLOCK = SIZE_OF_SUPER_BLOCK + SUM_OF_DATA_BLOCK // 8 + SUM_OF_INODE_BLOCK // 8 + SUM_OF_INODE_BLOCK \
                          * SIZE_OF_EACH_INODE_BLOCK
