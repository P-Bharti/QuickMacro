#!/usr/bin/env python3
import keyboard
import mouse
import threading
import time
import pickle
import argparse
'''
    To fix a issue in the library "mouse" set the _nixcommon.py code as the following if the mouse clicks, etc don't work (lines 31-33)
    UI_SET_KEYBIT = 0x40045565
    for i in range(0x115): # CHANGE ADDED: https://github.com/boppreh/mouse/issues/37#issuecomment-1672929057
        fcntl.ioctl(uinput, UI_SET_KEYBIT, i)
'''

keyboard_events = []
mouse_events = []
combined_events = []

end_recording_hotkey = "esc" # for custom bindings, either use the scan code of the key (56 for space for eg.) or in the format: ' ' or in the format 'space'
replay_speed = 1 # subject to change by parser in MACRO CLI PARSER section
move_relative = False # subject to change by function retrieve_recording_from_file() from MACRO FUCTIONS and by parser in MACRO CLI PARSER section

#  ----| MACRO FUCTIONS START |----

# - minor functions -
def keyboard_events_indexer():
    # similar to keyboard.record(), but with a few changes
    def append_event(event):
        nonlocal recorded
        recorded.append((event,(None,None))) # None says that the x and y coords are not taken for keyboard inputs (unlike mouse)

    recorded = []
    keyboard.hook(append_event)
    keyboard.wait(end_recording_hotkey)
    keyboard.unhook(append_event)
    recorded = recorded[:-1] # removes the esc exit key from events
    return recorded

def record_keyboard():
    global keyboard_events
    print("Recording keyboard... Press ESC to stop.")
    keyboard_events = keyboard_events_indexer()
    print("Keyboard recording stopped.")
    stop_mouse.set() # tells mouse_events_indexer() to stop recording

def mouse_events_indexer():
    # similar to mouse.record(), but with a few changes

    def append_event(event): # in trackpads, move ends up as an event unlike mouse; so storing x,y so we can manually move it if its confused (gives button type '?')
        nonlocal recorded
        recorded.append((event,mouse.get_position()))

    recorded = []
    # similar to mouse.wait(), but with a change to account for ending when keyboard stops
    mouse.hook(append_event)
    stop_mouse.wait()
    mouse.unhook(append_event)
    return recorded

def record_mouse():
    global mouse_events
    print("Recording mouse... Press ESC to stop.")
    mouse_events = mouse_events_indexer()
    print("Mouse recording stopped.")

# - MAJOR FUNCTION - Uses the four minor functions above to record the macro; Saves recording in keyboard_events list and mouse_events list
def begin_recording():
    global stop_mouse
    keyboard_thread = threading.Thread(target=record_keyboard)
    mouse_thread = threading.Thread(target=record_mouse)
    stop_mouse = threading.Event()

    print("Recording started... (ESC to end recording)")
    start_time = time.time()

    keyboard_thread.start()
    mouse_thread.start()

    keyboard_thread.join()
    mouse_thread.join()

    end_time = time.time()
    print("\nRecording finished! Duration: " + str(round(end_time - start_time,2)) + " seconds")

# - MAJOR FUNCTION - Merges both event lists, processes and prints the list "combined_events"
def combine_mouse_keyboard_records():
    global combined_events # will be a list of tuples in the format (source, timestamp, event, (pos_x,pos_y))

    for item in keyboard_events: # in the format of a tuple (event,(None,None))
        event = item[0]
        coordinates = item[1]
        combined_events.append(("keyboard", event.time, event, coordinates)) # None says that the x and y coords are not taken for keyboard inputs (obviously)

    if move_relative == True:
        for i in range(0,len(mouse_events)): # in the format of a tuple (event,(x_pos,y_pos))
            event = mouse_events[i][0]
            if i != 0:
                coordinates = mouse_events[i][1]
                prev_coordinates = mouse_events[i-1][1]
                x_coordinate = coordinates[0] - prev_coordinates[0]
                y_coordinate = coordinates[1] - prev_coordinates[1]
                coordinates = (x_coordinate,y_coordinate)
            else:
                coordinates = (0,0)
            combined_events.append(("mouse", event.time, event,coordinates))
    else:
        for item in mouse_events: # in the format of a tuple (event,(x_pos,y_pos))
            event = item[0]
            coordinates = item[1]
            combined_events.append(("mouse", event.time, event,coordinates))

    # sort by timestamp
    combined_events.sort(key=lambda x: x[1])

    # pretty printing the recording
    print("\n--- Combined Timeline ("+ str(len(combined_events)) + " events) ---")
    for source, timestamp, event, (pos_x,pos_y) in combined_events:
        print(str(round(timestamp,4)), source, event, str(pos_x) + "," + str(pos_y), sep = " | ")

# - MAJOR FUNCTION (pt. 1 of 2) - Saves the list "combined_events" to a txt file
def save_recording_to_file(file_name):
    file_writer = open(file_name + ".dat", "wb")

    if move_relative == False: # first line in file denotes whether mouse should move relative or not
        pickle.dump("ABSOLUTE_RECORDING",file_writer)
    else:
        pickle.dump("RELATIVE_RECORDING",file_writer)
    
    for i in combined_events:
        pickle.dump(i,file_writer)

    file_writer.close()

# - MAJOR FUNCTION (pt. 2 of 2) - Retrieves data from the txt file and sends to the list "combined_events"
def retrieve_recording_from_file(file_name):
    global combined_events, move_relative

    file_opener = open(file_name + ".dat", "rb")
    retrieved_lines = []

    recording_type = pickle.load(file_opener) # first line in file denotes whether mouse should move relative or not
    if recording_type == "ABSOLUTE_RECORDING":
        move_relative = False
    elif recording_type == "RELATIVE_RECORDING":
        move_relative = True
        
    try:
        while True:
            retrieved_lines.append(pickle.load(file_opener))
    except EOFError:
        pass

    file_opener.close()

    combined_events = retrieved_lines

# - minor function -
def detect_escape():
    keyboard.wait("esc") # will not progress till esc is hit
    escape_found.set()

# - MAJOR FUNCTION - Uses the one minor function above to detect early quit; Plays back the macro using the list "combined_events"
def playback_macro():
    global escape_found

    try: # combined_events in format (source, time, event, coordinates)
        first_t = combined_events[0][1] # orignially, first timestamp is the prev t
        first_coordinates = mouse_events[0][1] # mouse_events in the format of a tuple (event,(x_pos,y_pos))
    except IndexError:
        first_coordinates = (None,None) # if relative is chosen and mouse isnt moved; no need to do first_t as if no events then the for loop doesnt run
        print("\nNotice: You've either not entered any input or havent moved the mouse in the recording.")

    escape_detector = threading.Thread(target = detect_escape, daemon = True) # early exit detector
    escape_detector.start()
    escape_found = threading.Event()

    keyboard.release('space') # fixes a bug where the first letter isnt captured
    for source, t, event, (pos_x,pos_y) in combined_events:
        if escape_found.is_set():
            break

        delay = (t - first_t)/replay_speed
        first_t = t
        if delay > 0:
            time.sleep(delay)

        if source == "keyboard":
            if event.event_type == "down":
                keyboard.press(event.scan_code)
            elif event.event_type == "up":
                keyboard.release(event.scan_code)
        else:
            if move_relative == True:
                if isinstance(event, mouse.ButtonEvent) and event.button == "?":
                    mouse.move(pos_x,pos_y,absolute = False) # to bypass weird trackpad errors (janky, though)
                    
                elif isinstance(event, mouse.ButtonEvent): # doing manually to help dragging
                    if event.event_type == "down":
                        mouse.release(event.button)
                    elif event.event_type == "up":
                        mouse.press(event.button)

                elif isinstance(event, mouse.MoveEvent):
                    mouse.move(pos_x,pos_y,absolute = False)
                else: # scrolling doesnt work on ubuntu 24 - idk why
                    mouse.play([event])
            else:
                if isinstance(event, mouse.ButtonEvent) and event.button == "?":
                    mouse.move(pos_x,pos_y) # to bypass weird trackpad errors (janky, though)

                elif isinstance(event, mouse.ButtonEvent): # doing manually to help dragging
                    if event.event_type == "down":
                        mouse.release(event.button)
                    elif event.event_type == "up":
                        mouse.press(event.button)

                else: # scrolling doesnt work on ubuntu 24 - idk why
                    mouse.play([event])

    print("\nPlayback finished.")

# - minor functions - (wrappers)
def record_combine_save_recording(file_name):
    begin_recording()
    combine_mouse_keyboard_records()
    save_recording_to_file(file_name)

def load_play_recording(file_name):
    retrieve_recording_from_file(file_name)
    playback_macro()

#  ----| MACRO FUCTIONS END |----

#  ----| MACRO CLI PARSER START |----

parser = argparse.ArgumentParser(prog='QuickMacro',
                                 description="Record or playback recordings.")

# Global arguments: save file (-s [str]) and delay (-d [float])
parser.add_argument(
    "-s", "--save-file",
    type = str,
    default = "Recoding_1",
    help="File name of the recording WITHOUT file extention (default: Recording_1)."
)
parser.add_argument(
    "-d", "--delay",
    type = float,
    default = 3.0,
    help = "Seconds to wait before starting (default: 3.0)."
)

subparsers = parser.add_subparsers(dest="mode", required=True)

record_parser = subparsers.add_parser("record", help="Record actions")
# Recording subcommand: move relative (-mr)
record_parser.add_argument(
    "-mr", "--move-relative",
    action="store_true",
    default=False,
    help="Record moves relative to the starting point (default: False)."
)

playback_parser = subparsers.add_parser("playback", help="Playback actions")
# Playback subcommand: replay speed (-rs [float])
playback_parser.add_argument(
    "-rs", "--replay-speed",
    type=float,
    default=1.0,
    help="Delay divider for playback (default: 1.0)."
)

args = parser.parse_args()

if args.mode == "record":
    time.sleep(args.delay)
    move_relative = args.move_relative
    record_combine_save_recording(args.save_file)
elif args.mode == "playback":
    time.sleep(args.delay)
    replay_speed = args.replay_speed
    load_play_recording(args.save_file)

#  ----| MACRO CLI PARSER END |----

