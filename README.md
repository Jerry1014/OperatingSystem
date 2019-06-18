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
          command line 用户黑框界面 （输入检测，输出结果，多用户登录）
          
    - 杂七杂八
    
          语言初步定为python
          调用系统接口，创建一个大文件，并以此作为我们的虚拟硬盘
          在此之上通过read()/write()等，结合文件系统结构，实现模拟
        
  - todo
  
        写todo
