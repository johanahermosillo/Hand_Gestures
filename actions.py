# actions.py
"""
System actions for gesture control
"""
import subprocess
import platform
import os
import pyautogui


def open_myutep():
    """Open my.utep.edu in default browser"""
    url = "https://my.utep.edu"
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(['start', url], shell=True)
        elif system == "Darwin":
            subprocess.Popen(['open', url])
        else:
            subprocess.Popen(['xdg-open', url])
        print("Opened my UTEP")
    except Exception as e:
        print("Error opening UTEP:", e)


def open_spotify():
    """Open Spotify application"""
    print("Opening Spotify")
    try:
        os.system("start spotify")
    except Exception as e:
        print("Error opening Spotify:", e)


def change_volume(direction):
    """
    Change system volume
    Args:
        direction: "UP" or "DOWN"
    """
    system = platform.system()
    try:
        if system in ("Windows", "Darwin"):
            pyautogui.press("volumeup" if direction == "UP" else "volumedown")
        else:
            step = "5%+" if direction == "UP" else "5%-"
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", step])
    except Exception as e:
        print("Volume error:", e)