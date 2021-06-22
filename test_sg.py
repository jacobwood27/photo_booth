import cv2, PySimpleGUI as sg

window = sg.Window('Demo Application - OpenCV Integration', [[sg.Image(filename='', key='image')], ], location=(800, 400))
cap = cv2.VideoCapture("/dev/video1")  # Setup the camera as a capture device
while True:  # The PSG "Event Loop"
    event, values = window.read(timeout=20, timeout_key='timeout')  # get events for the window with 20ms max wait
    if event is None:  break  # if user closed window, quit
    window['image'].update(data=cv2.imencode('.png', cap.read()[1])[1].tobytes())  # Update image in window