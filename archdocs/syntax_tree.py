"""Reading a source through its syntax tree instead of through a regex.

The tree answers what a pattern can only guess at: whether a name is a call or a word in a
comment, which keyword belongs to which call, where a string starts and ends. The price is that a
file the running interpreter cannot parse gives no tree at all, so a feature read this way loses
that file, where a regex would still have matched something in it.
"""

import ast
import typing
import warnings


# The parse runs on every file of somebody's project, and an invalid escape in a regex literal is
# a `SyntaxWarning` printed into their logs on each scan: the filter is narrowed to the pseudo
# file name below, so warnings of the service's own code are left as they are.
_PARSED_FILE_NAME: typing.Final = "<archdocs>"
warnings.filterwarnings("ignore", category=SyntaxWarning, module=_PARSED_FILE_NAME)


def parse_syntax_tree(raw_source: str, /) -> ast.Module | None:
    try:
        return ast.parse(raw_source, filename=_PARSED_FILE_NAME)
    except (SyntaxError, ValueError, RecursionError):
        return None


# `ast.walk` goes breadth first, and a feature that takes the first match has to take the one
# written first, the way a regex search does.
def list_nodes_in_source_order(syntax_tree: ast.Module, /) -> list[ast.AST]:
    return sorted(
        ast.walk(syntax_tree),
        key=lambda one_node: (getattr(one_node, "lineno", 0), getattr(one_node, "col_offset", 0)),
    )


def read_callee_name(one_call: ast.Call, /) -> str:
    match one_call.func:
        case ast.Name(id=callee_name) | ast.Attribute(attr=callee_name):
            return callee_name
        case _:
            return ""


def read_imported_modules(one_node: ast.AST, /) -> tuple[str, ...]:
    match one_node:
        case ast.ImportFrom(module=str() as module_name):
            return (module_name,)
        case ast.Import(names=every_alias):
            return tuple(one_alias.name for one_alias in every_alias)
        case _:
            return ()
