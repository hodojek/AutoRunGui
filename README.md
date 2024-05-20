# AutoRunScript
This script uses directx scan codes to hold W+SHIFT for you if there isn't an option to toggle running in a game.

## Usage
Just run it and press the toggle key.

The script will hold W and SHIFT until the toggle key is pressed again.

## Running it
### Python
Install dependencies with:
```
python -m pip install -r requirements.txt
```

And run it with:
```
python src/main.py
```
### .EXE
Alternatively you can download the [auto_run_gui.exe](https://github.com/hodojek/AutoRunGui/releases) file and run that.
### Make your own executable
You can make your own executable with pyinstaller by running:
```
python -m pip install pyinstaller
```
```
pyinstaller auto_run_gui.spec
```
