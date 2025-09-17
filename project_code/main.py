import keyboard
import mouse
import threading
import time
'''
    To fix a issue in the library 'mouse' set the _nixcommon.py code as the following if the mouse clicks, etc don't work (lines 31-33)
    UI_SET_KEYBIT = 0x40045565
    for i in range(0x115): # CHANGE ADDED: https://github.com/boppreh/mouse/issues/37#issuecomment-1672929057
        fcntl.ioctl(uinput, UI_SET_KEYBIT, i)
'''

keyboard_events = []
mouse_events = []

def record_keyboard():
    global keyboard_events
    print("Recording keyboard... Press ESC to stop.")
    keyboard_events = keyboard.record(until = "esc")
    keyboard_events = keyboard_events[:-1] # removes the esc exit key from
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
    print("Recording mouse... Right click to stop.")
    mouse_events = custom_mouse_record()
    print("Mouse recording stopped.")

# main_code
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

for event in keyboard_events:
    combined_events.append(("keyboard", event.time, event, (None,None))) # None says that the x and y coords are not taken for keyboard inputs (obv)

for event in mouse_events:
    combined_events.append(("mouse", event[0].time, event[0],event[1]))

# sort by timestamp
combined_events.sort(key=lambda x: x[1])

print(f"\n--- Combined Timeline ("+ str(len(combined_events)) + " events) ---")
for source, timestamp, event, (pos_x,pos_y) in combined_events:
    print(str(round(timestamp,4)), source, event, str(pos_x) + "," + str(pos_y), sep = " | ")

# playing back the macro
print("\nReplaying in 3 seconds... Hold ESC to quit at any time!")
time.sleep(3)

start_playback = time.time()

prev_t = combined_events[0][1] # orignially, first timestamp is the prev t
replay_speed = 1
for src, t, ev, (pos_x,pos_y) in combined_events:
    if keyboard.is_pressed('esc'):
        break
    delay = (t - prev_t)/replay_speed # this makes it real time, but then the computer struggles to do combinations like shift-a
    prev_t = t
    if delay > 0:
        time.sleep(delay)

    if src == "keyboard":
        keyboard.play([ev])
    else:
        if isinstance(ev, mouse.ButtonEvent) and ev.button == "?":
            mouse.move(pos_x,pos_y) # to bypass weird trackpad errors (janky, though)
        else: # scrolling doesnt work on ubuntu 24 - idk why
            mouse.play([ev])

print("\nPlayback finished.")