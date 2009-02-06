from webskewer.http.serve import serve
from webskewer.http.static_files import static_files


def main():
    serve(static_files(u'.'))
