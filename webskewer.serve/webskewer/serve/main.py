from webskewer.serve.serve import serve
from webskewer.wsgi.static_files import static_files


def main():
    serve(static_files(u'.'))
