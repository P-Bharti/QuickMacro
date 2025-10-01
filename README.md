# QuickMacro

**QuickMacro** is a Python tool for recording and replaying mouse and keyboard actions.  
It uses the [`keyboard`](https://pypi.org/project/keyboard/) and [`mouse`](https://pypi.org/project/mouse/) libraries to capture user input and simulate playback.

* Strictly an automation tool; Do not attempt to use for games (it won't work anyways)
---

## Features
- **Record** mouse and keyboard actions simultaneously
- **Playback** recordings at adjustable speeds  
- (Hypothetially) Cross Platform
- Mouse animation on X11 (Linux)
- Rudementary trackpad support (move relative doesn't work)  

> Note that on linux, the script requires sudo (to access inputs without being X11 dependant) and on mac requires granting accessibility permissions to terminal/python in System Preferences -> Security & Privacy

---

## Installation

Clone the repository:

```
git clone https://github.com/P-Bharti/QuickMacro.git
cd QuickMacro
```
Install dependencies:
It is dependendant on the keyboard and mouse libraries, but they have been provided.
> Note that the mouse's nix_common file (and the same file thats in the keyboard library for some reason) has a change on line 32: for i in range(0x115): # CHANGE ADDED: https://github.com/boppreh/mouse/issues/37#issuecomment-1672929057

## Usage
QuickMacro provides a command-line interface (CLI) to record and playback actions.
It is recommended to save the command such that it runs via a hotkey of your design in your system settings. (so a hotkey to record and a hotkey to play)
<br>
For Example, the line might be:
```
bash -c "cd /path/to/QuickMacro && pkexec ./main.py -s [file_name] -d [delay] record [-mr only if you want relative motion]"
```
```
bash -c "cd /path/to/QuickMacro && pkexec ./main.py -s [file_name] -d [delay] playback -rs [replay speed]"
```
> The above commands would require a password each time when run; To avoid this, you can use the format below:
```
bash -c "cd /path/to/QuickMacro && export HISTIGNORE='*sudo -S*' && echo "your_root_password" | sudo -S ./main.py -s [file_name] -d [delay] record [-mr only if you want relative motion]"
```
```
bash -c "cd /path/to/QuickMacro && export HISTIGNORE='*sudo -S*' && echo "your_root_password" | sudo -S ./main.py -s [file_name] -d [delay] playback -rs [replay speed]"
```

> All These particular commands are for Ubuntu, and may be placed in the custom shortcut option in the settings (under keyboard at the end).

On *nix systems, you are required to chmod +x main.py via the terminal, or otherwise to make the script executable

## Global Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-s`, `--save-file` | `str` | `Recording_1` | File name for the recording (without extension).|
| `-d`, `--delay`     | `int` | `3`          | Seconds to wait before starting. |


and of course, --help or -h for help

## Record Arguments
Record mouse and keyboard actions (press ESC to end recording, or modify main.py's end_recording_hotkey to change):

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-mr`, `--move-relative` | `flag` | `False` | Record mouse moves relative to the starting point. |

EXAMPLE FOR WINDOWS (When terminal is in the directory of the script; otherwise write the path to it):
```
python main.py -s Recording_1 -d 3 record -mr
```
EXAMPLE FOR LINUX (When terminal is in the directory of the script; otherwise write the path to it):
```
sudo ./main.py -s Recording_1 -d 3 record -mr
```
EXAMPLE FOR UNIX (When terminal is in the directory of the script; otherwise write the path to it) (also terminal/python requires accessibility permissions in System Preferences -> Security & Privacy):
```
./main.py -s Recording_1 -d 3 record -mr
```
> Waits 3 seconds before starting, then records with relative mouse movement enabled.

## Playback Mode
Replay a saved recording:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-rs`, `--replay-speed` | `float` | `1.0` | Adjust playback delay divisor. |


EXAMPLE FOR WINDOWS (When terminal is in the directory of the script; otherwise write the path to it):
```
python main.py -s Recording_1 playback -rs 2
```
EXAMPLE FOR LINUX (When terminal is in the directory of the script; otherwise write the path to it):
```
sudo ./main.py -s Recording_1 -playback -rs 2
```
EXAMPLE FOR UNIX (When terminal is in the directory of the script; otherwise write the path to it) (also terminal/python requires accessibility permissions in System Preferences -> Security & Privacy):
```
./main.py -s Recording_1 playback -rs 2
```
> Plays the recording at double speed.

## License
This project is licensed under the MIT License.
See the LICENSE file for details.
