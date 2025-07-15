pyinstaller --onefile --windowed ^
    --name UnicodeChecker ^
    --add-data "C:\Windows\Fonts\seguiemj.ttf;." ^
    --add-data "C:\Windows\Fonts\seguisym.ttf;." ^
    --runtime-tmpdir=. ^
    --hidden-import=winreg ^
    --hidden-import=config ^
    --hidden-import=utils ^
    --hidden-import=gui ^
    --version-file=version_info.txt ^
    main.py