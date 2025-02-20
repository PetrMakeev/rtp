pyinstaller --name rtp --onefile --noconsole --add-data "icons;icons" --icon="icons/database.ico" main.py
copy dist\rtp.exe .