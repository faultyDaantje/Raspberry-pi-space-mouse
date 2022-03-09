import time
import analogio
from analogio import AnalogIn
import board
import busio as io
import digitalio
import usb_hid
import rotaryio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
import adafruit_framebuf
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import adafruit_ssd1306


#this encoder is used to control the sensivity of the spacemouse
encodersens = rotaryio.IncrementalEncoder(board.GP5, board.GP4)
last_sens = 0

kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

#x and y are switched on purpose, because of the way the spacemouse is placed.
y_axis = analogio.AnalogIn(board.A3)
x_axis = analogio.AnalogIn(board.A0)

#button inside the joystick works as a mouse click
Button = digitalio.DigitalInOut(board.GP0)
Button.direction = digitalio.Direction.INPUT
Button.pull = digitalio.Pull.UP

#button to choose what you want to change the sensitivity of
senstoggler = digitalio.DigitalInOut(board.GP1)
senstoggler.direction = digitalio.Direction.INPUT
senstoggler.pull = digitalio.Pull.UP

senstoggle = 0

Redo = digitalio.DigitalInOut(board.A2)
Redo.direction = digitalio.Direction.INPUT
Redo.pull = digitalio.Pull.UP

Undo = digitalio.DigitalInOut(board.A1)
Undo.direction = digitalio.Direction.INPUT
Undo.pull = digitalio.Pull.UP

#encoder on top of the joystick, for zooming in and out
encoder = rotaryio.IncrementalEncoder(board.GP7, board.GP6)
last_position = 0

i2c = io.I2C(board.GP3, board.GP2)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
potscroll = 5
potpan = 5
scrollspeed=(0.4 * potscroll)
pansens=(1 * potpan)
pot_min = 0.00
pot_max = 4.99
step = (pot_max - pot_min) / 40.0

#for updating the display
def display_reset(oled):
    oled.fill(0)
    oled.text('sensitivity:', 0, 0, 1)
    oled.text(str(potscroll)+'/5', 10, 22, 1)
    oled.text(str(potpan)+'/5', 74, 22, 1)
    oled.line(0, 10, 128, 10, 1)
    oled.line(64, 10, 64, 32, 1)
    oled.text('zoom:', 0, 11, 1)
    oled.text('pan:', 66, 11, 1)
    oled.line(0, 20, 128, 20, 1)
    oled.show()
def sens1(oled):
    oled.fill(0)
    oled.text('sensitivity:', 0, 0, 1)
    oled.text(str(potscroll)+'/5', 10, 22, 1)
    oled.text(str(potpan)+'/5', 74, 22, 1)
    oled.line(0, 10, 128, 10, 1)
    oled.line(64, 10, 64, 32, 1)
    oled.text('zoom:', 0, 11, 1)
    oled.text('pan:', 66, 11, 1)
    oled.line(0, 20, 128, 20, 1)
    oled.line(4, 30, 60, 30, 1)
    oled.show()
def sens2(oled):
    oled.fill(0)
    oled.text('sensitivity:', 0, 0, 1)
    oled.text(str(potscroll)+'/5', 10, 22, 1)
    oled.text(str(potpan)+'/5', 74, 22, 1)
    oled.line(0, 10, 128, 10, 1)
    oled.line(64, 10, 64, 32, 1)
    oled.text('zoom:', 0, 11, 1)
    oled.text('pan:', 66, 11, 1)
    oled.line(0, 20, 128, 20, 1)
    oled.line(68, 30, 124, 30, 1)
    oled.show()
def get_voltage(pin):
    return (pin.value * 5) / 65536

def steps(axis):
    """ Maps the potentiometer voltage range to 0-20 """
    return round((axis - pot_min) / step)

def is_joystick_active( x, y ):
    """Checks whether the joystick is away from the center position"""
    return steps(x) > 36.0 or steps(x) < 5.0 or steps(y) > 36.0 or steps(y) < 5.0
# def redo():
#     kbd.press(Keycode.CONTROL)
#     kbd.press(Keycode.Y)
#     kbd.release(Keycode.CONTROL)
#     kbd.release(Keycode.Y)
# def undo():
#     kbd.press(Keycode.CONTROL)
#     kbd.press(Keycode.Z)
#     kbd.release(Keycode.CONTROL)
#     kbd.release(Keycode.Z)
#     print(action)
def undoredo(action):
    #y = redo
    #z = redo
    kbd.press(Keycode.CONTROL)
    kbd.press(action)
    kbd.release(Keycode.CONTROL)
    kbd.release(action)

def updateoled():
    if senstoggle == 0:
        display_reset(oled)
    elif senstoggle == 1:
        sens1(oled)
    elif senstoggle == 2:
        sens2(oled)


def get_mouse_move( x, y ):
    """Translates x,y voltages into how far to move the mouse on each step"""
    mouse_x = 0;
    mouse_y = 0;
    if steps(x) > 36.0:
        # print(steps(x))
        mouse_x-=pansens

    if steps(x) < 5.0:
        # print(steps(y))
        mouse_x+=pansens

    if steps(y) > 36.0:
        # print(steps(y))
        mouse_y+=pansens

    if steps(y) < 5.0:
        # print(steps(y))
        mouse_y-=pansens
    return mouse_x, mouse_y

display_reset(oled)

sensposition = encodersens.position

deflection = 0


while True:
    #print(str(digitalio.DigitalInOut.value))
    x = get_voltage(x_axis)
    y = get_voltage(y_axis)
    scrollspeed=(0.4 * potscroll)
    pansens=(1 * potpan)
    

    sensposition = encodersens.position


  
    sens = sensposition + deflection
    
    
    if sens < 0:
        deflection = deflection + 1
    elif sens > 5:
        deflection = deflection - 1
#         if sensposition + deflection > 0 and sensposition + deflection < 10:
#             deflection = 0

    last_sens = sensposition
    if senstoggler.value is False:
        senstoggle = senstoggle + 1
        if senstoggle > 2:
            senstoggle = 0
        updateoled()
            
    while Undo.value is False:
        undoredo(Keycode.Z)
    else:
        kbd.release(Keycode.CONTROL)
        kbd.release(Keycode.Z)

    while Redo.value is False:
        undoredo(Keycode.Y)
    else:
        kbd.release(Keycode.CONTROL)
        kbd.release(Keycode.Y)
        
            
#     if senstoggle == 0:
#         display_reset(oled)    
#     elif senstoggle == 1:
#         sens1(oled)
#     elif senstoggle == 2:
#         sens2(oled)
    
    #time.sleep(0.5)
    if Button.value is False:
        mouse.click(Mouse.LEFT_BUTTON)
        
    if senstoggle == 1:
        if potscroll != sens:
            potscroll = sens
            updateoled()
    elif senstoggle == 2:
        if potpan != sens:
            potpan = sens
            updateoled()
        

    if is_joystick_active( x, y ):
        kbd.press(Keycode.SHIFT)
        mouse.press(Mouse.MIDDLE_BUTTON)

        while is_joystick_active( x, y ):
            mouse_x, mouse_y = get_mouse_move( x, y )
            mouse.move(x=mouse_x, y=mouse_y)
            # Wait for a bit
#             time.sleep(0.1)
            # Check the joystick position again
            x = get_voltage(x_axis)
            y = get_voltage(y_axis)
        else:
            kbd.release(Keycode.SHIFT)
            mouse.release(Mouse.MIDDLE_BUTTON)
    
    position = encoder.position
    scroll = position - last_position
    if last_position is None or position != last_position:
        """makes the encoder scroll the amount it turns"""
        mouse.move(wheel = int(scroll * scrollspeed))
        print(position)
    last_position = position
    