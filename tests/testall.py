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
    'webskewer.http',
    'webskewer.http.headers',
    'webskewer.http.log',
    'webskewer.http.main',
    'webskewer.http.message',
    'webskewer.http.multipart',
    'webskewer.http.range_util',
    'webskewer.http.recv',
    'webskewer.http.serve',
    'webskewer.http.static_files',
    'webskewer.http.status',
    'webskewer.http.time_util',
    'webskewer.http.util',
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
