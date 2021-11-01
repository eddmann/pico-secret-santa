import json
import time
import picodisplay as display
from allocator import allocate
from sim800l import SIM800L


display_width = display.get_width()
display_buffer = bytearray(display_width * display.get_height() * 2)
display.init(display_buffer)
display.set_backlight(0.8)


def clear_display():
    global display
    display.set_pen(255, 0, 0)
    display.clear()
    display.set_pen(255, 255, 255)


participants = json.loads(open("participants.json").read())

# Loading

clear_display()
display.text("Loading...", 10, 105, display_width - 10, 2)
display.update()

sim = SIM800L()

# Menu

clear_display()
display.text("Secret Santa Allocator", 10, 15, display_width - 10, 3)
display.text("Press B to Begin", 10, 105, display_width - 10, 2)
display.update()

while not display.is_pressed(display.BUTTON_B):
    time.sleep(0.5)

# Allocation

clear_display()
display.text("Allocating...", 10, 105, display_width - 10, 2)
display.update()

allocations = allocate(participants)
time.sleep(3)

# Sending

for (participant, recipient) in allocations:
    clear_display()
    display.text("Sending Secret Santa", 10, 15, display_width - 10, 2)
    display.text(participant['name'], 10, 55, display_width - 10, 4)
    display.update()
    message = "%s, you are Secret Santa for %s :)" % (
        participant['name'], recipient['name'])
    sim.send_sms(participant['number'], message)

# Complete

clear_display()
display.text("Allocation Complete", 10, 15, display_width - 10, 3)
display.text("Merry Christmas!", 10, 105, display_width - 10, 2)
display.update()
