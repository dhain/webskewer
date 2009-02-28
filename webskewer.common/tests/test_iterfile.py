import unittest

from webskewer.common.util import IterFile


class TestIterFile(unittest.TestCase):
    def test_read(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.read() == ''.join(it)
        assert iterfile.read() == ''
    
    def test_read_with_arg(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.read(9) == 'hello wor'
        assert iterfile.read(2) == 'ld'
        assert iterfile.read(6) == '!\ngood'
        assert iterfile.read(100) == 'bye world!'
        assert iterfile.read(1) == ''
    
    def test_readline(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.readline() == 'hello world!\n'
        assert iterfile.readline() == 'goodbye world!'
        assert iterfile.readline() == ''
        assert iterfile.read() == ''
    
    def test_readlines(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.readlines() == ['hello world!\n', 'goodbye world!']
        assert iterfile.readlines() == []
        assert iterfile.read() == ''
    
    def test_readlines_with_arg(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.readlines(1) == ['hello world!\n', 'goodbye world!']
        assert iterfile.readlines(100) == []
        assert iterfile.read() == ''
    
    def test_iter(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert list(iter(iterfile)) == ['hello world!\n', 'goodbye world!']
        assert list(iter(iterfile)) == []
        assert iterfile.read() == ''
    
    def test_close(self):
        it = ['hello ', 'world!', '\ngoodbye world!', '']
        iterfile = IterFile(it)
        assert iterfile.readline() == 'hello world!\n'
        iterfile.close()
        self.assertRaises(IOError, iterfile.read)
        self.assertRaises(IOError, iterfile.readline)
        self.assertRaises(IOError, iterfile.readlines)
        self.assertRaises(IOError, iter(iterfile).next)
        iterfile.close()


if __name__ == '__main__':
    unittest.main()
