from Input import *
from threading import Timer
import time
import ctypes

'''
When I made a knex handbrake I wanted it so that if I was holding down a letter
it would send a handbrake key, and when I let go it would send that key again
'''

_WORD = ctypes.c_ushort
_DWORD = ctypes.c_ulong
_LONG = ctypes.c_long
_ULONG_PTR = ctypes.POINTER(_DWORD)
_INPUT_MOUSE = 0
_INPUT_KEYBOARD = 1
_INPUT_HARDWARD = 2
_KEYEVENTF_KEYUP = 0x0002

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', _LONG),
                ('dy', _LONG),
                ('mouseData', _DWORD),
                ('dwFlags', _DWORD),
                ('time', _DWORD),
                ('dwExtraInfo', _ULONG_PTR))

class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', _DWORD),
                ('wParamL', _WORD),
                ('wParamH', _WORD))

class _KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", _WORD),  
                ("wScan", _WORD),
                ("dwFlags", _DWORD),
                ("time", _DWORD), 
                ("dwExtraInfo", _ULONG_PTR))

class _INPUTUNION(ctypes.Union):
    _fields_ = (('mi', _MOUSEINPUT),
                ('ki', _KEYBDINPUT),
                ('hi', _HARDWAREINPUT))

class _INPUT(ctypes.Structure):
    _fields_ = (('type', _DWORD),
               ('union', _INPUTUNION))

class HandBrake:
    def __init__(self,spammedLetter,handBrakeKey):
        self.pressedBefore=False
        self.handBrakeKey=handBrakeKey
        self.spammedLetter=spammedLetter
        self.started=False
        self.up=True
        Input.bind(spammedLetter,self.dummyFunction)
        Input.bindRelease(spammedLetter,self.releasedKey)

    def _sendVirtual(self,vk,press=True):
        keybdinput =_KEYBDINPUT(vk, ctypes.windll.user32.MapVirtualKeyA(vk, 0), 0 if press else _KEYEVENTF_KEYUP)
        input = _INPUT(_INPUT_KEYBOARD, _INPUTUNION(ki=keybdinput))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input), ctypes.sizeof(input))

    def pressKey(self,check):
        if self.pressedBefore==check:
            self._sendVirtual(self.handBrakeKey)
            self._sendVirtual(self.handBrakeKey,False)
            self.pressedBefore=False if check==True else True

    def releasedKey(self):
        if not self.up:
            self.liftUp()

    def liftUp(self):
        if self.up==False:
            self.pressKey(True)
            self.up=True

    def putDown(self):
        if self.up==True:
            self.pressKey(False)
            self.up=False

    def dummyFunction(self):
        if self.up:
            if not self.pressedBefore:
                self.putDown()
            
    def mainLoop(self):
        Input.mainLoop()


toggleKey=None
handbrakeKey=None
running=True

def key1(key):
    global handbrakeKey
    handbrakeKey=key
    Input.ignoreAll(key1)
    Input.bindAll(key2)
    print("Toggle Key?: ")

def key2(key):
    global toggleKey,running
    if key!=handbrakeKey:
        toggleKey=key
        running=False

print("Handbrake?: ")
Input.bindAll(key1)
while running:
    Input.checkBindings()
    time.sleep(0.01)

Input.ignoreAll(key2)

HandBrake(handbrakeKey,toggleKey).mainLoop()
