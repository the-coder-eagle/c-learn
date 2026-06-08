# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('content', 'content'),
        ('tools/tcc/tcc.exe', 'tools/tcc'),
        ('tools/tcc/libtcc.dll', 'tools/tcc'),
        ('tools/tcc/include', 'tools/tcc/include'),
        ('tools/tcc/lib', 'tools/tcc/lib'),
    ],
    hiddenimports=[
        'flask', 'webview', 'services', 'simulator',
        'yaml', 'pygments', 'pygments.lexers', 'pygments.lexers.c_cpp',
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='C-Learn', debug=False, strip=False, upx=True,
    runtime_tmpdir=None, console=False,
    target_arch=None, codesign_identity=None, entitlements_file=None,
)
