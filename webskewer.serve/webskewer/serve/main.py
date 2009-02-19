from webskewer.serve.serve import serve
from webskewer.serve.static_files import static_files


def main():
    serve(static_files(u'.'))
