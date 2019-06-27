# 操作系统实验和课程设计

## experiment 实验部分
    5states 模拟5状态转换
    page_replacement 模拟页面置换
    PS 消费者/生产者同步问题
    # ~ 没啥好食用的，就酱 ~
  
## curriculum design 课程设计 （未完成）
  - 题目 unix文件系统模拟
  - 大致结构
    
        VirtualHardDiskDriver 虚拟硬盘文件的“驱动程序”，负责文件的读写
        kernel 模拟内核，以块为单位，对硬盘进行读写控制
        command line 用户黑框界面 （输入检测，输出结果，用户登录）
        Main 程序入口，抽象的电源按键 （用于未来的多用户同时登录）
        Setting 保存超参数
        VirtualDiskVisualization 虚拟硬盘文件的可视化工具，用于辅助测试 *什么？我们竟然有测试？*
        KernelTest 简单unitest测试
        
  - 初步文件系统结构设计
  ![Image text](./miscellaneous/文件系统结构.png)
          
  - 内核部分
      - 通过from Kernel import my_kernel调用内核
      - 注意：此时**my_kernel**为内核的**实例**的单例化形式，非类名
      - 使用实例，可参考KernelTest中的测试
      - 提供的接口
          - [x] 添加文件或目录 add_directory_or_file(directory, data=None)
              - directory: 要添加的完整路径
                - 目录：形如/etc/psw/ **注意目录末尾的‘/’** 
                - 文件：形如/etc/psw/psw.txt
              - data: 对于文件来说，这是文件的内容 目录无此参数 类型为**bytes**
              - return: None
              - raise: NotADirectory(检查输入的路径) FileOrDirectoryToBig(文件系统限制)
          - [x] 删除目录或文件 remove_directory_or_file(directory)
            - directory 与添加文件或目录中的directory相同
            - raise: NotADirectory FileNotFoundError (检查输入的路径)
          - [x] 读取目录 read_directory_or_file(directory)
              - directory 与添加文件或目录中的directory相同
              - return:
                - 文件：str 文件内容
                - 目录：list 目录下所有的目录/文件名列表
              - raise: NotADirectory FileNotFoundError (检查输入的路径)
          - [x] 查看硬盘状态 show_disk_state()
            - return: tuple 卷名(char)  最后挂载时间(float) 块大小(int) inode块大小(int) 总块数(int) 空闲块数(int) /
            - /总inode块数(int) 空闲inode块数(int)
          - [x] 获得节点（文件/目录）信息 get_directory_file_info(directory)
            - directory 与添加文件或目录中的directory相同
            - return 元组 元组内数据见Setting.INODE_BLOCK_STRUCT
            - raise: NotADirectory FileNotFoundError (检查输入的路径)
          - [x] 创建硬链接 add_hard_link(directory, aim_directory):
            - directory：完整路径 添加快捷方式到此路径
            - aim_directory：完整路径 源文件
          - [x] 关闭内核 shut_down()
              - **！重要！在关闭前必须执行此操作，否则可能会导致虚拟硬盘文件未关闭或缓冲数据未写入文件的问题**
          
    
  - 用户界面部分
    - 通过CommandLine通过调用内核接口来实现
        - _current_directory 是用来记录当前的路径
        - login_in() 登录方法，在CommandLine实例化时，通过调用此方法进行用户验证登录
        - parse_user_input() 用于解析用户命令
            - 例如说，用户现在输入了'ls /ect' 这个字符串传到了这个方法里的user_input里
            - 暂时略过权限的检查部分
            - 我们简单分割就能得到 命令是ls 参数是 /ect
            - 这时，我们通过调用
                - my_kernel.read_directory_or_file(command_list[1] if len(command_list) > 1 else self._current_directory)
                - 来返回这个目录下的文件列表并输出
                - my_kernel.read_directory_or_file 用于读取文件和目录，此时读取的是目录
                - command_list[1] if len(command_list) > 1 else self._current_directory 用于用户只输入ls时，输出工作目录的结果
    - todo
      - [x] 添加删除用户 修改登录密码
        - [x] useradd
        - [x] userdel
        - [x] passwd
      - [x] 基本命令
        - [x] df
        - [x] mkdir
        - [x] ls
        - [x] rm
        - [x] cat        
        - [x] mv
        - [x] creat
        - [x] cd
        - [x] pwd
        - [x] cp
        - [x] link
        - [x] mkfs
      - [ ] 文件读写权限检查
      - [ ] 高级命令
        - [ ] chmod
        - [ ] find
