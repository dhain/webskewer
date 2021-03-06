import unittest
import doctest


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def mod_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


modules = (
    'webskewer.serve',
    'webskewer.serve.headers',
    'webskewer.serve.log',
    'webskewer.serve.main',
    'webskewer.serve.message',
    'webskewer.serve.multipart',
    'webskewer.serve.recv',
    'webskewer.serve.serve',
)

test_modules = (
)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    doc_suite = unittest.TestSuite()
    for m in modules:
        mod = mod_import(m)
        doc_suite.addTest(doctest.DocTestSuite(mod))
    suite.addTests(doc_suite)
    for m in test_modules:
        mod = mod_import(m)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
