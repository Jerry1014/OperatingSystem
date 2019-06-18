"""
工程入口
"""
import traceback

from Kernel import kernel
from CommandLine import ui

print('启动中...')
all_users_thread = list()

while True:
    try:
        choice = int(input('1.新用户登录\n'
                           '0.退出\n'))
        if choice == 0:
            break
        elif choice == 1:
            # 多用户有点点难搞，先一个一个用户的来吧
            ui()
    except Exception as e:
        # print('非法输入')

        # 调试用，验收时删除traceback输出，替换为上句
        traceback.print_exc()
