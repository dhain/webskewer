import unittest

from webskewer.common.util import DummyFile


class TestDummyFile(unittest.TestCase):
    def test_read(self):
        dummyfile = DummyFile()
        assert dummyfile.read() == ''
    
    def test_read_with_arg(self):
        dummyfile = DummyFile()
        assert dummyfile.read(9) == ''
        assert dummyfile.read(1) == ''
    
    def test_readline(self):
        dummyfile = DummyFile()
        assert dummyfile.readline() == ''
    
    def test_readlines(self):
        dummyfile = DummyFile()
        assert dummyfile.readlines() == []
    
    def test_readlines_with_arg(self):
        dummyfile = DummyFile()
        assert dummyfile.readlines(100) == []
    
    def test_iter(self):
        dummyfile = DummyFile()
        assert list(iter(dummyfile)) == []
    
    def test_close(self):
        dummyfile = DummyFile()
        assert dummyfile.read() == ''
        dummyfile.close()
        self.assertRaises(IOError, dummyfile.read)
        self.assertRaises(IOError, dummyfile.readline)
        self.assertRaises(IOError, dummyfile.readlines)
        self.assertRaises(IOError, iter(dummyfile).next)
        dummyfile.close()


if __name__ == '__main__':
    unittest.main()
