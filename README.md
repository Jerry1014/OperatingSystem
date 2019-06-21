# 操作系统实验和课程设计

## experiment 实验部分
    5states 模拟5状态转换
    page_replacement 模拟页面置换
    PS 消费者/生产者同步问题
    # ~ 没啥好食用的，就酱 ~
  
## curriculum design 课程设计 （未完成）
  - 题目 unix文件系统模拟
  - 初步构想
    - 大致结构
        - kernel 模拟内核的基本文件读写操作（增删读写文件，虚拟硬盘的格式化挂载等）
        - command line 用户黑框界面 （输入检测，输出结果，用户登录）
        - Main 程序入口，抽象的电源按键 （新用户新黑窗）
        - Setting 保存超参数
        - VirtualDiskVisualization 虚拟硬盘文件的可视化工具，用于辅助测试 *什么？我们竟然有测试？*
        
    - 运行逻辑

          Main入口，单例kernel实例化，虚拟硬盘初始化
          选择用户登录
          每一个用户一个黑窗用以输入 （多线程？进程？）
          CommandLine类调用kernel读取/ect/users下的内容获得用户和密码 若无 则提示创建root账户
          登录验证过后，用户的输入通过CommandLine解析，并调用内核执行相应操作

    - 初步文件系统结构设计
          ![Image text](./miscellaneous/文件系统结构.png)
          
          **文件系统使用方法**
            ！f = kernel._virtual_disk_file 不要重复打开文件，文件句柄在单例kernel中
          
          1.块位图
            f.seek(Setting.START_OF_DATA_BLOCK_BITMAP)
            tem = struct.unpack('I',f.read(4)[0]) 读取一个unsign int 32位 每一位对应一个块 0为可用
            tem = format(bin(tem),'032b') 可通过此方法，将tem转为32个二进制的 01字符串 ！str！
            然后逐次判读tem[i] == '1'即可 若无，则继续读下一三十二位，注意不要越界
          2.节点位图基本同上
            f.seek(Setting.START_OF_INODE_BLOCK_BITMAP)
          3.节点块
            f.seek(START_OF_INODE_BLOCK)
            tem = struct.unpack(Setting.INODE_BLOCK_STRUCT,f.read(Setting.SIZE_OF_EACH_INODE_BLOCK)) 读取一个inode块
            inode块结构定义已经写好，在Setting.INODE_BLOCK_STRUCT中
            此时返回的tem为元组，里面数据参见上方结构图，按需取用即可
          4.数据块
             f.seek(START_OF_DATA_BLOCK)
                
          其他：
            以上f的偏移量计算均为到某个区域块的初始位置
            在此之上根据节点id/数据块id计算偏移量，小学生难度，再问挨打
            VirtualDiskVisualization.py完成了硬盘文件的可视化，对块访问不理解的，可看代码
            上述脚本也可用于debug，在完成功能后，记得调用可视化工具查看硬盘文件是否符合预期

    - 杂七杂八
    
          语言初步定为python
          调用系统接口，创建一个大文件，并以此作为我们的虚拟硬盘
          在此之上通过read()/write()等，结合文件系统结构，实现模拟
    
  - todo
    - [ ] 增加目录
        - [ ] 完成硬盘的根目录和/etc路径初始化
    - [ ] 增加文件
        - [ ] 实现用户登录
    - [ ] 删除文件/目录