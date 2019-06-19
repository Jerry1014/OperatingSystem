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
        
          kernel 模拟内核的基本文件读写操作（增删读写文件，虚拟硬盘的格式化挂载等）
          command line 用户黑框界面 （输入检测，输出结果，用户登录）
          Main 程序入口，抽象的电源按键 （新用户新黑窗）
          
    - 运行逻辑

          Main入口，单例kernel实例化，虚拟硬盘初始化
          选择用户登录
          每一个用户一个黑窗用以输入 （多线程？进程？）
          CommandLine类调用kernel读取/ect/users下的内容获得用户和密码 若无 则提示创建root账户
          登录验证过后，用户的输入通过CommandLine解析，并调用内核执行相应操作

    - 杂七杂八
    
          语言初步定为python
          调用系统接口，创建一个大文件，并以此作为我们的虚拟硬盘
          在此之上通过read()/write()等，结合文件系统结构，实现模拟
    
  - todo
  
        写todo
