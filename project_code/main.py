import keyboard
import mouse
import threading
import time # TODO hotkey to activate (menu)
'''
    To fix a issue in the library 'mouse' set the _nixcommon.py code as the following if the mouse clicks, etc don't work (lines 31-33)
    UI_SET_KEYBIT = 0x40045565
    for i in range(0x115): # CHANGE ADDED: https://github.com/boppreh/mouse/issues/37#issuecomment-1672929057
        fcntl.ioctl(uinput, UI_SET_KEYBIT, i)
'''

keyboard_events = []
mouse_events = []

replay_speed = 1 # TODO get into menu (zero for instant)
move_relative = False # TODO get into menu

def custom_keyboard_record():
    # similar to keyboard.record(), but with a few changes
    def append_event(event): # TODO add hotkey support for stuff like shift+a
        nonlocal recorded
        recorded.append((event,(None,None))) # None says that the x and y coords are not taken for keyboard inputs (unlike mouse)

    recorded = []
    keyboard.hook(append_event)
    keyboard.wait("esc")
    keyboard.unhook(append_event)
    recorded = recorded[:-1] # removes the esc exit key from events
    return recorded

def record_keyboard():
    global keyboard_events
    print("Recording keyboard... Press ESC to stop.")
    keyboard_events = custom_keyboard_record()
    print("Keyboard recording stopped.")
    stop_mouse.set() # tells custom_mouse_record() to stop recording

def custom_mouse_record():
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
    mouse_events = custom_mouse_record()
    print("Mouse recording stopped.")

# recording the macro
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

# merging into one list named combined_events
combined_events = []

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

print("\n--- Combined Timeline ("+ str(len(combined_events)) + " events) ---")
for source, timestamp, event, (pos_x,pos_y) in combined_events:
    print(str(round(timestamp,4)), source, event, str(pos_x) + "," + str(pos_y), sep = " | ")

def detect_escape():
    keyboard.wait("esc") # will not progress till esc is hit
    escape_found.set()

# playing back the macro
print("\nReplaying in 3 seconds... Press ESC to quit at any time!")
time.sleep(3)

try: # combined_events in format (source, time, event, coordinates)
    first_t = combined_events[0][1] # orignially, first timestamp is the prev t
    first_coordinates = mouse_events[0][1] # mouse_events in the format of a tuple (event,(x_pos,y_pos))

except IndexError:
    print("\nNo events detected!")

escape_detector = threading.Thread(target = detect_escape, daemon = True) # exit detector
escape_detector.start()
escape_found = threading.Event()

for source, t, event, (pos_x,pos_y) in combined_events:
    if escape_found.is_set():
        break

    delay = (t - first_t)/replay_speed # this makes it real time, but then the computer struggles to do combinations like shift-a
    first_t = t
    if delay > 0:
        time.sleep(delay)

    if source == "keyboard":
        keyboard.play([event])
    else:
        if move_relative == True:
            if isinstance(event, mouse.ButtonEvent) and event.button == "?":
                mouse.move(pos_x,pos_y,absolute = False) # to bypass weird trackpad errors (janky, though)
            if isinstance(event, mouse.MoveEvent):
                mouse.move(pos_x,pos_y,absolute = False)
            else: # scrolling doesnt work on ubuntu 24 - idk why
                mouse.play([event])
        else:
            if isinstance(event, mouse.ButtonEvent) and event.button == "?":
                mouse.move(pos_x,pos_y) # to bypass weird trackpad errors (janky, though)
            else: # scrolling doesnt work on ubuntu 24 - idk why
                mouse.play([event])

print("\nPlayback finished.")

