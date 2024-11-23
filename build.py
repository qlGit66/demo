import PyInstaller.__main__

def build():
    PyInstaller.__main__.run([
        'main.py',
        '--name=超星自动答题',
        '--windowed',
        '--onefile',
        '--hidden-import=PyQt5',
        '--hidden-import=selenium',
        '--hidden-import=webdriver_manager',
        '--hidden-import=requests',
        '--hidden-import=websocket-client',
        '--clean',
        '--noconfirm'
    ])

if __name__ == '__main__':
    build() 