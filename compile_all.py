import py_compile
import os

root = os.path.dirname(__file__)
errors = []
for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if f.endswith('.py'):
            path = os.path.join(dirpath, f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append((path, str(e)))

if errors:
    print('Compilation errors found:')
    for p, msg in errors:
        print(p)
        print(msg)
    raise SystemExit(1)
else:
    print('All python files compiled successfully.')
