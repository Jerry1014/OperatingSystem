import os
import unittest

from VirtualDiskVisualization import visualization


class KernelTest(unittest.TestCase):
    # def test_tem(self):
    #     if os.path.exists('my_virtual_hard_disk'):
    #         os.remove('my_virtual_hard_disk')
    #
    #     from Kernel import kernel
    #     for i in range(20):
    #         kernel._find__free_inode_block()
    #         kernel._find__free_data_block(3)
    #     kernel.shut_down()
    #     visualization('my_virtual_hard_disk')
    #
    def test_for_add_file_or_directory_from_init(self):
        if os.path.exists('my_virtual_hard_disk'):
            os.remove('my_virtual_hard_disk')

        from Kernel import kernel
        kernel.add_directory_or_file('/etc/')
        kernel.add_directory_or_file('/etc/psw/')
        kernel.add_directory_or_file('/etc/psw/psw.txt', b'12345678')
        kernel.shut_down()
        visualization('my_virtual_hard_disk')


if __name__ == '__main__':
    unittest.main()