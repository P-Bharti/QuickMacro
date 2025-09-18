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

> Note that on linux, the script requires sudo (to access inputs without being X11 dependant) and on mac requires granting accessibility permissions to terminal/python in System Preferences -> Security & Privacy

---

## Installation

Clone the repository:

```
git clone https://github.com/yourusername/QuickMacro.git
cd QuickMacro
```
Install dependencies:

```
pip install keyboard mouse
```
## Usage
QuickMacro provides a command-line interface (CLI) to record and playback actions.
It is recommended to save the command such that it runs via a hotkey of your design in your system settings. (so a hotkey to record and a hotkey to play)

## Global Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-s`, `--save-file` | `str` | `Recording_1` | File name for the recording (without extension).|
| `-d`, `--delay`     | `int` | `3`          | Seconds to wait before starting. |


and of course, --help or -h for help

## Record Arguments
Record mouse and keyboard actions:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-mr`, `--move-relative` | `flag` | `False` | Record mouse moves relative to the starting point. |

Example:

```
python main.py -s Recording_1 -d 3 record -mr
```
> Waits 3 seconds before starting, then records with relative mouse movement enabled.

## Playback Mode
Replay a saved recording:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-rs`, `--replay-speed` | `float` | `1.0` | Adjust playback delay divisor. |


Example:
```
python main.py -s Recording_1 playback -rs 2
```
> Plays the recording at double speed.

## License
This project is licensed under the MIT License.
See the LICENSE file for details.
