# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Quote board matrix display
# uses AdafruitIO to serve up a quote text feed and color feed
# random quotes are displayed, updates periodically to look for new quotes
# avoids repeating the same quote twice in a row

import time
import displayio
import board
import digitalio
from adafruit_matrixportal.matrixportal import MatrixPortal
import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.polygon import Polygon

# --- Display setup ---
matrixportal = MatrixPortal(
    status_neopixel=board.NEOPIXEL, debug=True, width=32, height=16
)
display = matrixportal.display


# --- Drawing setup ---
# Create a Group
group = displayio.Group()
# Create a bitmap object
bitmap = displayio.Bitmap(32, 16, 2)  # width, height, bit depth
# Create a color palette
color = displayio.Palette(4)
color[0] = 0x000000  # black
color[1] = 0xFF0000  # red
color[2] = 0x444444  # dim white
color[3] = 0xDD8000  # gold
# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
# Add the TileGrid to the Group
group.append(tile_grid)

# draw the frame for startup
rect1 = Rect(0, 0, 2, 16, fill=color[2])
rect2 = Rect(30, 0, 2, 16, fill=color[2])
rect3 = Rect(1, 0, 4, 2, fill=color[0])
rect4 = Rect(27, 0, 4, 2, fill=color[0])
rect5 = Rect(1, 14, 6, 2, fill=color[0])
rect6 = Rect(24, 14, 6, 2, fill=color[0])

group.append(rect1)
group.append(rect2)
group.append(rect3)
group.append(rect4)
group.append(rect5)
group.append(rect6)


def redraw_frame():  # to adjust spacing at bottom later
    rect3.fill = color[2]
    rect4.fill = color[2]
    rect5.fill = color[2]
    rect6.fill = color[2]


# draw the wings w polygon shapes
wing_polys = []

wing_polys.append(Polygon([(2, 3), (7, 3), (7, 4), (3, 4)], outline=color[1]))
wing_polys.append(Polygon([(4, 6), (7, 6), (7, 7), (5, 7)], outline=color[1]))
wing_polys.append(Polygon([(5, 9), (7, 9), (7, 10), (6, 10)], outline=color[1]))
wing_polys.append(Polygon([(23, 3), (29, 3), (23, 4), (28, 4)], outline=color[1]))
wing_polys.append(Polygon([(23, 6), (27, 6), (23, 7), (26, 7)], outline=color[1]))
wing_polys.append(Polygon([(23, 9), (25, 9), (23, 10), (24, 10)], outline=color[1]))

for wing_poly in wing_polys:
    group.append(wing_poly)


# text positions
on_x = 11
on_y = 4
off_x = 10
off_y = 4
air_x = 9
air_y = 10



# --- Content Setup ---
deco_font = bitmap_font.load_font("/04B_03__6pt.bdf")

text_line1 = adafruit_display_text.label.Label(deco_font, color=color[3], text="OFF")
text_line1.x = off_x
text_line1.y = off_y

text_line2 = adafruit_display_text.label.Label(deco_font, color=color[1], text="AIR")
text_line2.x = air_x
text_line2.y = air_y


# Put each line of text into the Group
group.append(text_line1)
group.append(text_line2)


def redraw_wings(index):  # to change colors
    for wing in wing_polys:
        wing.outline = color[index]


def startup_text():
    text_line1.text = "Shy"
    text_line1.x = 10
    text_line1.color = color[2]
    text_line2.text = ".Dev"
    text_line2.x = 2
    text_line2.color = color[2]
    redraw_wings(0)
    display.root_group = group


startup_text()  # display the startup text

def update_text(state):
    if state:  # if switch is on, text is "ON" at startup
        text_line1.text = "ON"
        text_line1.x = on_x
        text_line1.color = color[1]
        text_line2.text = "AIR"
        text_line2.x = air_x
        text_line2.color = color[1]
        redraw_wings(1)
        redraw_frame()
        display.root_group = group
    else:  # else, text if "OFF" at startup
        display.root_group = None


btn = digitalio.DigitalInOut(board.A1)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.DOWN


def get_status():
    """
    Get on off status.

    Return true for testing.
    """
#    return btn.value
    return True


mode_state = get_status()
update_text(mode_state)

last_check = None
while True:
    if last_check is None or time.monotonic() > last_check + 1:
        try:
            status = get_status()
            if status:
                if mode_state == 0:  # state has changed, toggle it
                    update_text(1)
                    mode_state = 1
            else:
                if mode_state == 1:
                    update_text(0)
                    mode_state = 0
            print("On Air:", status)
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
