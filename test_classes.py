from PySimpleGUI.PySimpleGUI import Text
import cv2
import PySimpleGUI as sg
import time
import os
import mediapipe as mp
import numpy as np
import imutils
import random
import copy


# Define some constants
PICTURES = {
    "logo"          : "pics/logo.png",
    "logo_portait"  : "pics/logo_color_portrait.png",
    "logo_landscape": "pics/logo_color_landscape.png",
    "flip_cover"    : "pics/flipbook_cover.png",
    "background"    : "pics/bg.png",
    "strip_dummy"   : "pics/bg_320_240.png",
    "cam_dummy"     : "pics/bg_1280_960.png",
    "hug_pic"       : "pics/jacob_02.png"
}

JACOB_PICS = [
    "pics/jacob_02.png",
]
ERIN_PICS = [
    "pics/erin_01.png",
]

PDF_W = 215.9       #mm, width of letter paper
PDF_H = 279.4       #mm, height of letter paper
CAM_X = 640         #pix, horizontal resolution of camera
CAM_Y = 480         #pix, vertical resolution of camera
SCREEN_X = 1920     #pix, horizontal resolution of screen
SCREEN_Y = 1200     #pix, vertical resolution of screen
UNPADDABLE = 7      #pix, remaining unpaddable pixels on edge of screen
FONT     = "Ariel"  #font for all the gui stuff

BUTTON_COLOR_OFF = ("white", "grey")
BUTTON_COLOR_ON = ("white", "green")

CAMERA_STREAM = "/dev/video0"

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

HIGH_SCORE_TODAY = 0
HIGH_SCORE_HOLDER = None

# class Picture:
#     def __init__(self, filename):
#         self.file = filename
#         self.im = cv2.imread(filename)
#         self.x = self.im.shape[1]
#         self.y = self.im.shape[2]


class ToggleButton(sg.Button):
    color_off = BUTTON_COLOR_OFF
    color_on = BUTTON_COLOR_ON
    def __init__(self, text, size, font, key, state=False):
        if state:
            col = self.color_on
        else:
            col = self.color_off
        super().__init__(text, size=size, font=font, key=key, button_color=col)
        self.state = state
        self.key = key
    def toggle(self, gui):
        gui[self.key].state = not gui[self.key].state 
        if gui[self.key].state:
            gui[self.key].Update(button_color=BUTTON_COLOR_ON)
        else:
            gui[self.key].Update(button_color=BUTTON_COLOR_OFF)

def get_landing_layout():

    opts = ['PHOTOSTRIP', 'FLIPBOOK', 'STORYBOOK', 'VIDEO']

    but_size = (10,4)
    fnt_size = 32

    fnt = (FONT, fnt_size)

    score_col = sg.Column([[sg.Text("Score", font=fnt, key='HIGH_SCORE_KEY', justification='r')],
                           [sg.Text("Score", font=fnt, key='CUR_SCORE_KEY',  justification='r')]], background_color='red', justification='r')
    layout = [  
        [sg.Text('Welcome to Our Photobooth!', font=fnt), score_col],
        [sg.Image(filename=PICTURES['cam_dummy'], key="landing_im")], 
        [sg.Text('What do you want to make today?', font=fnt)],
        [sg.Button(t, size = but_size, font=fnt) for t in opts]
    ]
    return layout




def get_photostrip_layout():
    small_but_size = (20,2)
    big_but_size = (25,3)
    fnt_size = 16
    fnt = (FONT, fnt_size)
    big_fnt_size = 30
    big_fnt = (FONT, big_fnt_size)

    v_pad = (SCREEN_Y - 2*UNPADDABLE - 4*240) / 8
    h_pad = (SCREEN_X - 2*UNPADDABLE - 2*640 - 320 - 20) / 4
    photostrip_col = [[sg.Image(filename=PICTURES['strip_dummy'], key='strip_im_'+str(i), pad=(h_pad,v_pad))] for i in range(4)]

    layout = [[
        sg.Column(  [[sg.Image(filename=PICTURES['cam_dummy'], pad=(h_pad,0), size=(2*640, 2*480), key='strip_im_main')], 
                    [ToggleButton(t, small_but_size, fnt, l) for (t,l) in zip(["Black and White", "Sketch", "Style"],["ps_bw", "ps_k", "ps_y"])],
                    [sg.Button("Click me when you are ready!",size = big_but_size, font=big_fnt, key="ps_ready")]], 
                    element_justification='c', pad=(0,0)), #background_color='blue'
        sg.Column(  photostrip_col, 
                    pad=(0,0), element_justification='c', justification='r') #, background_color='red')
        ]]

    return layout

def add_overlay(im1, im2, x, y):
    sx = im2.shape[1]
    sy = im2.shape[0]

    bx = im1.shape[1]
    by = im1.shape[0]

    sA = im2[:, :, 3] / 255.0
    bA = 1.0 - sA

    bx1 = x
    bx2 = x + sx
    by1 = y
    by2 = y + sy

    sx1 = 0
    sx2 = sx
    sy1 = 0
    sy2 = sy

    if bx1 < 0:
        bx1 = 0
        sx1 = -x
        
    if bx2 > bx:
        sx2 = sx - (bx2-bx)
        bx2 = bx

    if by1 < 0:
        by1 = 0
        sy1 = -y
        
    if by2 > by:
        sy2 = sy - (by2-by)
        by2 = by
    
    if by2<by1:
        by2=by1
    if bx2<bx1:
        bx2=bx1

    if sy2<sy1:
        sy2=sy1
    if sx2<sx1:
        sx2=sx1

    for c in range(0, 3):
        im1[by1:by2, bx1:bx2, c] = (sA[sy1:sy2, sx1:sx2] * im2[sy1:sy2, sx1:sx2, c] + bA[sy1:sy2, sx1:sx2] * im1[by1:by2, bx1:bx2, c])


def open_gui(LAYOUT_LIST):
    layout = [[sg.Column(lo, key=k, visible=False, element_justification='c') for (k,lo) in LAYOUT_LIST]]
    gui_window = sg.Window('Erin & Jacob Photobooth', layout, element_justification='c', resizable = True, margins=(0,0))
    gui_window.read(1)
    gui_window.maximize()
    return gui_window

def wait_gui(gui, sleeptime = 25):
    while True:
        event, values = gui.read(sleeptime)
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED:
            return -1
        elif event != "__TIMEOUT__":
            return event


class TrackedFace:
    def __init__(self, points):
        self.live = True
        self.points = points
        c_c, c_rad, c_rot = self.ear_circle()
        self.c_c = c_c
        self.c_rad = c_rad
        self.c_rot = c_rot
        self.X = c_c[0]
        self.Y = c_c[1]
        self.dia = 2*c_rad
    def still_alive(self):
        self.live = True
    def reset(self):
        self.live = False
    def ear_circle(self, face_bigger=1.2):
        lx = self.points[4][0] * CAM_X
        ly = self.points[4][1] * CAM_Y
        rx = self.points[5][0] * CAM_X
        ry = self.points[5][1] * CAM_Y
        dia = np.math.sqrt((lx-rx)**2 + (ly-ry)**2)
        rad = face_bigger * dia/2
        c = (round((lx+rx)/2), round((ly+ry)/2))
        rot = np.arctan2(ly-ry,lx-rx)
        return c, rad, rot

class FlyingHead:
    def __init__(self, P_t, image, rad, s_a, a = 10, w_max = 60, head_scale = 0.8):

        Xt = P_t[0]
        Yt = P_t[1]
        dia = round(2*rad)

        pix_avail = CAM_X + 2*Yt
        pix_select = np.random.randint(0,pix_avail)
        if pix_select < Yt:
            Xi = -dia
            Yi = Yt - pix_select
            Ai = np.random.rand() * 3.14/3
        elif pix_select < Yt + CAM_X:
            Yi = -dia
            Xi = pix_select - Yt
            if Xi < Xt:
                Ai = np.random.rand() * 3.1416/4
            else:
                Ai = 3.1415 - np.random.rand() * 3.14/4
        else:
            Xi = CAM_X + dia
            Yi = pix_select - CAM_X - Yt
            Ai = 3.14 - np.random.rand() * 3.14/3

        dX = Xt - Xi
        dY = Yt - Yi

        
        v = np.math.sqrt(0.5*a*dX**2/(np.math.cos(Ai)**2)/(dY + dX*np.math.tan(Ai)))
        
        self.X = Xi
        self.Y = Yi
        self.Vx = v * np.math.cos(Ai)
        self.Vy = -v * np.math.sin(Ai)
        self.a = a
        self.im = cv2.resize(cv2.imread(image, -1), (dia, dia))
        self.dia = dia * head_scale
        self.rad_px = round(dia/2)
        self.w = -w_max + 2*w_max*np.random.rand()
        self.thet = np.random.rand() * 360
        self.stuck = False
        self.track = None
        self.stuck_d = None
        self.stuck_thet = None
        self.orig_rot = None
        self.points = s_a

    def move(self, dt):
        if self.stuck and self.track.live:
            xt = self.track.X
            yt = self.track.Y
            thet = self.stuck_thet + (self.track.c_rot-self.orig_rot)

            d = self.stuck_d
            X_new = xt + d*np.math.cos(thet)
            Y_new = yt + d*np.math.sin(thet)
            self.Vx = (X_new - self.X) /dt
            self.Vy = (Y_new - self.Y) /dt
            self.X = X_new
            self.Y = Y_new
            self.thet = self.orig_rot_thet - (self.track.c_rot-self.orig_rot)*57.3
        
        else:
            self.stuck = False
            self.X += self.Vx * dt
            self.Y += self.Vy * dt
            self.Vy += self.a * dt
            self.thet += self.w * dt
        
    def near(self, track, thresh=1.0):
        x1 = self.X
        y1 = self.Y
        x2 = track.X
        y2 = track.Y
        return np.math.sqrt((x2-x1)**2 + (y2-y1)**2) < thresh*(self.dia+track.dia)/2
    
    def pos(self):
        return (round(self.X), round(self.Y))
    
    def draw(self, frame):
        add_overlay(frame, imutils.rotate(self.im, self.thet), round(self.X-self.rad_px), round(self.Y-self.rad_px))

    def stick(self, track):
        self.stuck = True
        self.track = track

        x1 = self.X
        y1 = self.Y
        x2 = track.X
        y2 = track.Y
        self.stuck_d = np.math.sqrt((x2-x1)**2 + (y2-y1)**2)
        thet = np.arctan2(y1-y2,x1-x2)
        self.stuck_thet = thet
        self.orig_rot_thet = self.thet
        self.orig_rot = track.c_rot


def run_landing(gui):
    gui['LANDING_LAYOUT'].update(visible=True)

    cheat = True

    cap = cv2.VideoCapture(CAMERA_STREAM)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    tt = 5
    t_start = time.time()

    track_list = []
    head_list = []
    last_time = time.time()

    head_size_min = 30
    head_size_max = 50

    score = 0

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:

        while True:
            event, values = gui.read(25)
            
            ret,frame = cap.read()
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = face_detection.process(image)
            for track in track_list:
                track.reset()


            cur_time = time.time()
            loop_dt = cur_time - last_time
            last_time = cur_time

            

            if results.detections:
                for detection in results.detections:
                    kp = [(d.x, d.y) for d in detection.location_data.relative_keypoints]
                    lx = kp[4][0] * CAM_X
                    ly = kp[4][1] * CAM_Y
                    rx = kp[5][0] * CAM_X
                    ry = kp[5][1] * CAM_Y
                    cx = (lx+rx)/2
                    cy = (ly+ry)/2

                    
                    max_thresh = 1.0
                    best_thresh = max_thresh*2
                    best_track = None
                    for face in track_list:
                        tx = face.X
                        ty = face.Y
                        tr = face.c_rad
                        d = np.math.sqrt((tx-cx)**2 + (ty-cy)**2)
                        n_d = d/tr
                        if n_d < best_thresh:
                            best_thresh = n_d
                            best_track = face
                    if best_thresh < max_thresh: #Then we will call the face the same
                        best_track.still_alive()
                        best_track.X = round(cx)
                        best_track.Y = round(cy)
                        best_track.c_c = (round(cx),round(cy))
                        best_track.c_rot = np.arctan2(ly-ry,lx-rx)
                        best_track.dia = np.math.sqrt((lx-rx)**2 + (ly-ry)**2)
                   
                    else: #new track
                        best_track = TrackedFace(kp)
                        track_list.append(best_track)

                    if cheat:
                        mp_drawing.draw_detection(frame, detection)
                        cv2.circle(frame, best_track.c_c, round(best_track.c_rad), (255,0,0)) 
                        lx = round(best_track.X + best_track.c_rad*np.cos(best_track.c_rot))
                        ly = round(best_track.Y + best_track.c_rad*np.sin(best_track.c_rot))
                        cv2.circle(frame, (lx, ly), 8, (255,0,0), -1) 
                
                p_spawn = 0.1
                if np.random.rand() < p_spawn and len(head_list)<10:
                    targ = random.choice(track_list)
                    if np.random.rand() > 0.5:
                        face_pic = random.choice(JACOB_PICS)
                        s_a = -2
                    else:
                        face_pic = random.choice(ERIN_PICS)
                        s_a = 1
                    head_size = head_size_min + (head_size_max-head_size_min)*random.random()
                    head_list.append(FlyingHead(targ.c_c, face_pic, head_size, s_a, a=20))

            points = 0
            for head in head_list:
                head.move(loop_dt)
                if head.Y > CAM_Y:
                    head_list.remove(head)
                    continue

                if not head.stuck:
                    for track in track_list:
                        if head.near(track):
                            head.stick(track)
                            break
                
                if not head.stuck:
                    for head2 in head_list:
                        if head2.stuck and head.near(head2):
                            head.stick(head2.track)
                            break
                
                if head.stuck:
                    points += head.points
                    

                head.draw(frame)
                if cheat:
                    cv2.circle(frame, head.pos(), round(head.dia/2), (255,0,255)) 

            print(points)

            for track in track_list:
                if not track.live:
                    track_list.remove(track)
                    

            gui['landing_im'].update(data=cv2.imencode('.png', cv2.resize(frame,(2*640, 2*480)))[1].tobytes())  # Update image in window

            if event != "__TIMEOUT__":
                break

    cap.release()
    gui['LANDING_LAYOUT'].update(visible=False)

    if event == sg.WINDOW_CLOSED:
            return -1
    else:
        dir = "output/" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + "_" + event
        os.mkdir(dir)
        return event, dir

def run_photostrip(gui, dir):
    gui['PHOTOSTRIP_LAYOUT'].update(visible=True)
    
    cap = cv2.VideoCapture(CAMERA_STREAM)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:

        while True:
            event, values = gui.read(25)
            
            ret,frame = cap.read()
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(cv2.resize(frame, (0,0), fx=1, fy=1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = face_detection.process(image)
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

            gui['strip_im_main'].update(data=cv2.imencode('.png', cv2.resize(frame,(2*640, 2*480)))[1].tobytes())  # Update image in window

            if event == sg.WINDOW_CLOSED:
                break
            elif event == "ps_bw":
                gui["ps_bw"].toggle(gui)
            elif event == "ps_k":
                gui["ps_k"].toggle(gui)
            elif event == "ps_y":
                gui["ps_y"].toggle(gui)
            
    cap.release()
    gui['PHOTOSTRIP_LAYOUT'].update(visible=False)
    

def run_photobooth():

    # Need to put all the layouts upfront and put them on the gui (hidden)
    LAYOUT_LIST = [
        ('LANDING_LAYOUT',    get_landing_layout()),
        ('PHOTOSTRIP_LAYOUT', get_photostrip_layout()),
        ]

    DISPATCH_DICT = {
        'LANDING'    : run_landing,
        'PHOTOSTRIP' : run_photostrip,
    }

    # Then make the window and get it spooled up
    gui = open_gui(LAYOUT_LIST)

    # Now we run the landing page
    selection, out_dir = DISPATCH_DICT['LANDING'](gui)

    # Now dispatch on the selection
    DISPATCH_DICT[selection](gui, out_dir)
    

run_photobooth()

