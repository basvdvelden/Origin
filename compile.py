from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("board",  ["chess/board.py"]),
    Extension("chess_functions",  ["chess/chess_functions.py"]),
    Extension("node",  ["origin/node.py"]),
    Extension("match",  ["chess/match.py"]),
    Extension("moves",  ["chess/moves.py"]),
    Extension("queries",  ["database/queries.py"]),
    Extension("database",  ["database/database.py"]),
    Extension("king_attacking_line",  ["chess/king_attacking_line.py"]),
    Extension("settings",  ["settings.py"]),
    Extension("origin", ["origin/origin.py"]),
    Extension("main", ["main.py"]),
]
setup(
    name='Origin',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules
)

