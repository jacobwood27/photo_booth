from fpdf import FPDF
import cv2
import time
import PySimpleGUI as sg
import os
import subprocess

logo_file = "/home/woojac/proj/019_photobooth_flipbook/pics/logo.png"
flip_cover_file = "/home/woojac/proj/019_photobooth_flipbook/pics/flipbook_cover.png"
bg_file = "/home/woojac/proj/019_photobooth_flipbook/pics/bg.png"
logo_im = cv2.imread(logo_file)
logo_dims = logo_im.shape


pdf_w=215.9
pdf_h=279.4
cam_res_x = 640
cam_res_y = 480
logo_res_x = logo_dims[1]
logo_res_y = logo_dims[0]

select_flag = ''

gui_page1_layout = [  
    [sg.Text('Welcome to Our Photobooth!')],
    [sg.Image(filename=logo_file, key='image')], 
    [sg.Text('What do you want to make today?')],
    [sg.Button('Photostrip'), sg.Button('Flipbook'), sg.Button('Storybook')]
]
gui_window = sg.Window('Erin & Jacob Photobooth', gui_page1_layout, element_justification='c')

# Display and interact with the Window using an Event Loop

while True:
    event, values = gui_window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Photostrip':
        select_flag = 'PHOTOSTRIP'
        print("Photostrip selected")
        gui_window.Close()
        break
    elif event == 'Flipbook':
        select_flag = 'FLIPBOOK'
        print("Flipbook selected")
        gui_window.Close()
        break
    elif event == 'Storybook':
        select_flag = 'STORYBOOK'
        print("Storybook selected")
        gui_window.Close()
        break



class PhotoStrip(FPDF):
    s_w = 0.8/3 * pdf_w
    s_s_h= 0.05 * pdf_w
    s_s_t = s_s_h

    f_w = s_w * 0.9
    f_h = f_w * cam_res_y/cam_res_x
    f_s = s_w * 0.05

    logo_s = 1*f_s
    logo_h = 1.0 * f_h
    logo_w = logo_h * logo_res_x / logo_res_y

    s_h = 4*f_h + 5*f_s + 2*logo_s + logo_h

    def draw_outside_borders(self):
        self.rect(self.s_s_h, self.s_s_t, self.s_w, self.s_h,'D')
        self.rect(2*self.s_s_h + self.s_w, self.s_s_t, self.s_w, self.s_h,'D')
        self.rect(3*self.s_s_h + 2*self.s_w, self.s_s_t, self.s_w, self.s_h,'D')

    def draw_inside_borders(self):
        for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
            self.rect(dx + self.s_s_h + self.f_s, self.s_s_t + self.f_s, self.f_w, self.f_h, 'D')
            self.rect(dx + self.s_s_h + self.f_s, self.s_s_t + 2*self.f_s + 1*self.f_h, self.f_w, self.f_h, 'D')
            self.rect(dx + self.s_s_h + self.f_s, self.s_s_t + 3*self.f_s + 2*self.f_h, self.f_w, self.f_h, 'D')
            self.rect(dx + self.s_s_h + self.f_s, self.s_s_t + 4*self.f_s + 3*self.f_h, self.f_w, self.f_h, 'D')

    def put_in_images(self, ims):
        for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
            self.image(ims[0], dx + self.s_s_h + self.f_s, self.s_s_t + self.f_s, self.f_w, self.f_h)
            self.image(ims[1], dx + self.s_s_h + self.f_s, self.s_s_t + 2*self.f_s + 1*self.f_h, self.f_w, self.f_h)
            self.image(ims[2], dx + self.s_s_h + self.f_s, self.s_s_t + 3*self.f_s + 2*self.f_h, self.f_w, self.f_h)
            self.image(ims[3], dx + self.s_s_h + self.f_s, self.s_s_t + 4*self.f_s + 3*self.f_h, self.f_w, self.f_h)
    
    def put_in_logo(self):
        for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
            self.image(logo_file, dx + self.s_s_h + self.s_w/2 - self.logo_w/2, self.s_s_t + self.s_h - self.logo_s - self.logo_h, self.logo_w, self.logo_h)

    def put_in_bg(self):
        for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
            self.image(bg_file, dx + self.s_s_h, self.s_s_t, self.s_w, self.s_h)




class FlipBook(FPDF):
    b_h = 0.9 * pdf_w
    m_v= (pdf_w - b_h)/2
    m_h = m_v
    b_w = pdf_h - 2*m_h

    f_w = b_w/4
    f_h = b_h/5

    i_h = f_h
    i_w = f_h * cam_res_x/cam_res_y

    num_h = f_w-i_w

    print(str(f_w), ", ", str(f_h), ", ", str(f_w/f_h))

    # f_w = s_w * 0.9
    # f_h = f_w * cam_res_y/cam_res_x
    # f_s = s_w * 0.05

    # logo_s = 1*f_s
    # logo_h = 1.0 * f_h
    # logo_w = logo_h * logo_res_x / logo_res_y

    # s_h = 4*f_h + 5*f_s + 2*logo_s + logo_h

    def draw_outside_borders(self):
        self.rect(self.m_h, self.m_v, self.b_w, self.b_h,'D')

    def draw_inside_borders(self):
        for ii in range(5):
            for jj in range(4):
                self.rect(self.m_h + jj*self.f_w, self.m_v + ii*self.f_h, self.f_w, self.f_h, 'D')

    def write_numbers(self):
        self.set_font('Arial', 'B', 16)
        for ii in range(5):
            for jj in range(4):
                num = ii + jj*5
                if num == 0:
                    continue
                x_coord = self.m_h + jj*self.f_w 
                y_coord = self.m_v + ii*self.f_h + self.f_h/2 
                self.text(x_coord, y_coord, "  " + str(num))
    
    def put_in_images(self, ims):
        for ii in range(5):
            for jj in range(4):
                num = ii + jj*5
                if num == 0:
                    x_coord = self.m_h 
                    y_coord = self.m_v 

                    self.image(ims[num], x_coord, y_coord, self.f_w, self.f_h)
                else:
                    x_coord = self.m_h + jj*self.f_w + self.num_h
                    y_coord = self.m_v + ii*self.f_h 

                    self.image(ims[num], x_coord, y_coord, self.i_w, self.i_h)
    
    # def put_in_logo(self):
    #     for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
    #         self.image(logo_file, dx + self.s_s_h + self.s_w/2 - self.logo_w/2, self.s_s_t + self.s_h - self.logo_s - self.logo_h, self.logo_w, self.logo_h)

    # def put_in_bg(self):
    #     for dx in [0, self.s_w+self.s_s_h, 2*self.s_w+2*self.s_s_h]:
    #         self.image(bg_file, dx + self.s_s_h, self.s_s_t, self.s_w, self.s_h)





if select_flag == 'PHOTOSTRIP':
    # #Simple photostrip

    photostrip_col = [
        [sg.Image(filename=logo_file, key='im1', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im2', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im3', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im4', size=(160,120))]
    ]
    gui_photostrip_layout = [  
        [sg.Image(filename=logo_file, size=(640, 480), key='image'), sg.Column(photostrip_col)], 
        [sg.Button("Click me when you are ready!"), sg.Button("Black and White"), sg.Button("Sketch"), sg.Button("Stylize")],
        [sg.Column([[sg.Text(size=(10,1), font=('Helvetica', 100), justification='c', key='-TTT-')],], justification='c')],
        [sg.Column([[sg.Text("FPS = 30  ", key="-FPS-")],], justification='r')]
    ]
    gui_window = sg.Window('Erin & Jacob Photobooth', gui_photostrip_layout, finalize=True)

    cap = cv2.VideoCapture("/dev/video1")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    idx = 1

    taking_flag = False
    bw_flag = False
    sketch_flag = False
    stylize_flag = False

    last_time = time.time()
    ttt = 5

    while(idx < 5):
        ret,frame = cap.read()
        frame = cv2.flip(frame, 1)

        if sketch_flag:
            frame1, frame2 = cv2.pencilSketch(frame)
            if bw_flag:
                frame = frame1
            else:
                frame = frame2
        elif bw_flag:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if stylize_flag:
            frame = cv2.stylization(frame)
            
        cur_time = time.time()
        d_time = cur_time - last_time
        fps_calc = 1/d_time
        last_time = cur_time 

        gui_window['-FPS-'].update("FPS = " + str(round(fps_calc)))

        event, values = gui_window.read(timeout=20)  # get events for the window with 20ms max wait
        if event is None:  break  # if user closed window, quit
        gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        if event == "Click me when you are ready!" and (not taking_flag):
            t_last_snap = time.time()
            taking_flag = True
        elif event == 'Black and White':
            bw_flag = ~bw_flag
        elif event == 'Sketch':
            sketch_flag = ~sketch_flag
        elif event == 'Stylize': #y for stYlize
            stylize_flag = ~stylize_flag 

        if taking_flag:
            cur_time = time.time()
            time_elapsed = cur_time - t_last_snap
            time_left = ttt-time_elapsed
            if time_left > 0.5:
                gui_window['-TTT-'].update(str(round(time_left)))
            elif time_left  > 0:
                gui_window['-TTT-'].update('Cheese!')
            else:
                gui_window['-TTT-'].update('Cheese!')
                subprocess.Popen("mpg123 -q /home/woojac/proj/019_photobooth_flipbook/camera_shutter.mp3", shell=True)
                cv2.imwrite("/home/woojac/proj/019_photobooth_flipbook/pics/" + str(idx) + ".png", frame)
                gui_window['im'+str(idx)].update(data=cv2.imencode('.png', cv2.resize(frame, (160,120)) )[1].tobytes())  # Update image in window
                t_last_snap = time.time()
                idx += 1

    gui_window.Close()
    cap.release()

    gui_photostrip_preview_layout = [  
            [sg.Image(filename="", size=(640, 480), key='image')], 
            [sg.Text(size=(20,1), font=('Helvetica', 30), justification='c', key='-TTT-')],
            [sg.Text("Do we like it?")],
            [sg.Button("Yep. Print please!"), sg.Button("Nah. Scrap it.")]
        ]
    gui_window = sg.Window('Erin & Jacob Photobooth - PhotStrip Preview', gui_photostrip_preview_layout, finalize=True, element_justification='c')


    ims = ["/home/woojac/proj/019_photobooth_flipbook/pics/" + str(i) + ".png" for i in [1,2,3,4]]


    pdf = PhotoStrip('P','mm','Letter')
    pdf.add_page()
    pdf.draw_outside_borders()
    pdf.put_in_bg()
    # pdf.draw_inside_borders()
    pdf.put_in_images(ims)
    pdf.put_in_logo()

    pdf.output('test.pdf','F')


    frame_time = 0.5
    last_time = time.time()
    cur_frame = 0
    while True:

        cur_time = time.time()
        if cur_time - last_time > frame_time:
            cur_frame += 1
            if cur_frame == 4:
                cur_frame = 0
            last_time = time.time()
            gui_window['-TTT-'].update(str(cur_frame+1) + "/4")
            frame = cv2.imread(ims[cur_frame])
            gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        event, values = gui_window.read(timeout=20)
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Nah. Scrap it.":
            break
        elif event == "Yep. Print please!":
            #implement send pdf to printer
            break
            
    gui_window.Close()


elif select_flag == "FLIPBOOK":

    flipbook_col = [
        [sg.Image(filename=logo_file, key='im1', size=(160,120)), sg.Image(filename=logo_file, key='im2', size=(160,120)), sg.Image(filename=logo_file, key='im3', size=(160,120)), sg.Image(filename=logo_file, key='im4', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im5', size=(160,120)), sg.Image(filename=logo_file, key='im6', size=(160,120)), sg.Image(filename=logo_file, key='im7', size=(160,120)), sg.Image(filename=logo_file, key='im8', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im9', size=(160,120)), sg.Image(filename=logo_file, key='im10', size=(160,120)), sg.Image(filename=logo_file, key='im11', size=(160,120)), sg.Image(filename=logo_file, key='im12', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im13', size=(160,120)), sg.Image(filename=logo_file, key='im14', size=(160,120)), sg.Image(filename=logo_file, key='im15', size=(160,120)), sg.Image(filename=logo_file, key='im16', size=(160,120))], 
        [sg.Image(filename=logo_file, key='im17', size=(160,120)), sg.Image(filename=logo_file, key='im18', size=(160,120)), sg.Image(filename=logo_file, key='im19', size=(160,120))], 
    ]
    
    gui_flipbook_layout = [  
        [sg.Image(filename=logo_file, size=(640, 480), key='image'), sg.Column(flipbook_col)], 
        [sg.Button("Click me when you are ready!"), sg.Button("Black and White"), sg.Button("Sketch"), sg.Button("Stylize")],
        [sg.Column([[sg.Text(size=(20,1), font=('Helvetica', 100), justification='c', key='-TTT-')],], justification='c')],
        [sg.Column([[sg.Text("FPS = 30  ", key="-FPS-")],], justification='r')]
    ]


    gui_window = sg.Window('Erin & Jacob Photobooth - Flipbook', gui_flipbook_layout, finalize=True)

    cap = cv2.VideoCapture("/dev/video1")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    idx = 1

    taking_flag = False
    bw_flag = False
    sketch_flag = False
    stylize_flag = False

    last_time = time.time()
    t_first_time = 5
    ttt = 1

    while(idx < 20):
        ret,frame = cap.read()
        frame = cv2.flip(frame, 1)

        if sketch_flag:
            frame1, frame2 = cv2.pencilSketch(frame)
            if bw_flag:
                frame = frame1
            else:
                frame = frame2
        elif bw_flag:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if stylize_flag:
            frame = cv2.stylization(frame)
            
        cur_time = time.time()
        d_time = cur_time - last_time
        fps_calc = 1/d_time
        last_time = cur_time 

        gui_window['-FPS-'].update("FPS = " + str(round(fps_calc)))

        event, values = gui_window.read(timeout=20)  # get events for the window with 20ms max wait
        if event is None:  break  # if user closed window, quit
        gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        if event == "Click me when you are ready!" and (not taking_flag):
            t_last_snap = time.time()
            taking_flag = True
        elif event == 'Black and White':
            bw_flag = ~bw_flag
        elif event == 'Sketch':
            sketch_flag = ~sketch_flag
        elif event == 'Stylize': #y for stYlize
            stylize_flag = ~stylize_flag 

        if taking_flag:
            cur_time = time.time()
            time_elapsed = cur_time - t_last_snap
            time_left = ttt-time_elapsed
            if idx == 1 and t_first_time - time_elapsed > 0.5:
                gui_window['-TTT-'].update(str(round(t_first_time - time_elapsed )))
            elif time_left > 0.5:
                gui_window['-TTT-'].update('Cheese! ' + str(idx) + "/" + "19")
            else:
                gui_window['-TTT-'].update('Cheese! ' + str(idx) + "/" + "19")
                subprocess.Popen("mpg123 -q /home/woojac/proj/019_photobooth_flipbook/camera_shutter.mp3", shell=True)
                cv2.imwrite("/home/woojac/proj/019_photobooth_flipbook/pics/" + str(idx) + ".png", frame)
                gui_window['im'+str(idx)].update(data=cv2.imencode('.png', cv2.resize(frame, (160,120)) )[1].tobytes())  # Update image in window
                t_last_snap = time.time()
                idx += 1

    cap.release()
    gui_window.Close()
    

    gui_flipbook_preview_layout = [  
            [sg.Image(filename="", size=(640, 480), key='image')], 
            [sg.Text(size=(20,1), font=('Helvetica', 30), justification='c', key='-TTT-')],
            [sg.Text("Do we like it?")],
            [sg.Button("Yep. Print please!"), sg.Button("Nah. Scrap it.")]
        ]
    gui_window = sg.Window('Erin & Jacob Photobooth - Flipbook Preview', gui_flipbook_preview_layout, finalize=True, element_justification='c')

    ims = ["/home/woojac/proj/019_photobooth_flipbook/pics/" + str(i) + ".png" for i in range(1,20)]
    ims.insert(0, flip_cover_file)

    pdf = FlipBook('L','mm','Letter')
    pdf.add_page()
    pdf.draw_outside_borders()

    pdf.write_numbers()
    pdf.put_in_images(ims)
    pdf.draw_inside_borders()

    pdf.output('test.pdf','F')

    frame_time = 0.2
    last_time = time.time()
    cur_frame = 1
    while True:

        cur_time = time.time()
        if cur_time - last_time > frame_time:
            cur_frame += 1
            if cur_frame == 20:
                cur_frame = 1
            last_time = time.time()
            gui_window['-TTT-'].update(str(cur_frame) + "/19")
            frame = cv2.imread(ims[cur_frame])
            gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        event, values = gui_window.read(timeout=20)
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Nah. Scrap it.":
            break
        elif event == "Yep. Print please!":
            #implement send pdf to printer
            break
            
    gui_window.Close()




elif select_flag == 'STORYBOOK':
    # #Simple photostrip

    ld = (160,120)
    storybook_col = [[sg.Image(filename=logo_file, key='im'+str(jj+ii), size=ld) for ii in [0,1,2,3]] for jj in [1,5,9,13]]
    
    gui_storybook_layout = [  
        [sg.Image(filename=logo_file, size=(640, 480), key='image'), sg.Column(storybook_col)], 
        [sg.Button("Click me to take the picture!"), sg.Button("Black and White"), sg.Button("Sketch"), sg.Button("Stylize")],
        [sg.Column([[sg.Text(size=(20,1), font=('Helvetica', 100), justification='c', key='-TTT-')],], justification='c')],
        [sg.Column([[sg.Text("  FPS = 30", key="-FPS-")],], justification='r')]
    ]

    gui_window = sg.Window('Erin & Jacob Photobooth', gui_storybook_layout, finalize=True)

    cap = cv2.VideoCapture("/dev/video1")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    idx = 1

    taking_flag = False
    bw_flag = False
    sketch_flag = False
    stylize_flag = False

    last_time = time.time()
    ttt = 0.5

    while(idx < 17):
        break
        ret,frame = cap.read()
        frame = cv2.flip(frame, 1)

        f_over = cv2.imread("/home/woojac/proj/019_photobooth_flipbook/sb1/1.png", -1)


        if sketch_flag:
            frame1, frame2 = cv2.pencilSketch(frame)
            if bw_flag:
                frame = frame1
            else:
                frame = frame2
        elif bw_flag:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if stylize_flag:
            frame = cv2.stylization(frame)

        # frame = cv2.addWeighted(frame, 0.5, f_over, 0.5, 0.0)
        alpha_s = f_over[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            frame[:, :, c] = (alpha_s * f_over[:, :, c] +
                              alpha_l * frame[:, :, c])
            
        cur_time = time.time()
        d_time = cur_time - last_time
        fps_calc = 1/d_time
        last_time = cur_time 

        gui_window['-FPS-'].update("FPS = " + str(round(fps_calc)))

        event, values = gui_window.read(timeout=20)  # get events for the window with 20ms max wait
        if event is None:  break  # if user closed window, quit
        gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        if event == "Click me to take the picture!" and (not taking_flag):
            t_last_snap = time.time()
            taking_flag = True
        elif event == 'Black and White':
            bw_flag = ~bw_flag
        elif event == 'Sketch':
            sketch_flag = ~sketch_flag
        elif event == 'Stylize': #y for stYlize
            stylize_flag = ~stylize_flag 

        if taking_flag:
            cur_time = time.time()
            time_elapsed = cur_time - t_last_snap
            time_left = ttt-time_elapsed
            if time_left > 0.5:
                gui_window['-TTT-'].update(str(round(time_left)))
            elif time_left  > 0:
                gui_window['-TTT-'].update('Cheese!')
            else:
                gui_window['-TTT-'].update('Cheese!')
                subprocess.Popen("mpg123 -q /home/woojac/proj/019_photobooth_flipbook/camera_shutter.mp3", shell=True)
                cv2.imwrite("/home/woojac/proj/019_photobooth_flipbook/pics/" + str(idx) + ".png", frame)
                cv2.imwrite("/home/woojac/proj/019_photobooth_flipbook/pics/" + str(idx) + "_small.png", cv2.resize(frame, (160,120)))
                gui_window['im'+str(idx)].update(data=cv2.imencode('.png', cv2.resize(frame, (160,120)) )[1].tobytes())  # Update image in window
                t_last_snap = time.time()
                taking_flag = False
                idx += 1
                gui_window['-TTT-'].update('')

    gui_window.Close()
    cap.release()

    gui_photostrip_preview_layout = [  
            [sg.Image(filename="", size=(640, 480), key='image')], 
            [sg.Button("Previous"), sg.Text(size=(20,1), font=('Helvetica', 30), justification='c', key='-TTT-'), sg.Button("Next")],
            [sg.Text("Do we like it?")],
            [sg.Button("Yep. Print please!"), sg.Button("Nah. Scrap it.")]
        ]

    ld = (160,120)
    storybook_col = [[sg.Image(filename="/home/woojac/proj/019_photobooth_flipbook/pics/" + str(jj+ii) + "_small.png", key='im'+str(jj+ii), size=ld, background_color='yellow') for ii in [0,1,2,3]] for jj in [1,5,9,13]]

    # lo2 = [sg.Column(gui_photostrip_preview_layout), sg.Column([storybook_col,])]
    lo2 = [[sg.Column(gui_photostrip_preview_layout, element_justification='c'), sg.Column(storybook_col)]]

    gui_window = sg.Window('Erin & Jacob Photobooth - PhotStrip Preview', lo2, finalize=True, element_justification='c', use_default_focus=False)


    ims = ["/home/woojac/proj/019_photobooth_flipbook/pics/" + str(i) + ".png" for i in range(1,17)]


    pdf = PhotoStrip('P','mm','Letter')
    pdf.add_page()
    pdf.draw_outside_borders()
    pdf.put_in_bg()
    # pdf.draw_inside_borders()
    pdf.put_in_images(ims)
    pdf.put_in_logo()

    pdf.output('test.pdf','F')



    cur_frame = 0
    while True:

        if cur_frame == 0:
            txt = "Front Cover"
        elif cur_frame == 15:
            txt = "Back Cover"
        else:
            txt = "Page " + str(cur_frame) + "/14"
        gui_window['-TTT-'].update(txt)
        gui_window['im' + str(cur_frame+1)].set_size(size = (1.05*ld[0], 1.05*ld[1]))

        frame = cv2.imread(ims[cur_frame])
        gui_window['image'].update(data=cv2.imencode('.png', frame)[1].tobytes())  # Update image in window

        event, values = gui_window.read(timeout=20)
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Previous":
            gui_window['im' + str(cur_frame+1)].set_size(size = ld)
            if cur_frame == 0:
                cur_frame = 15
            else:
                cur_frame -= 1
        elif event == "Next":
            gui_window['im' + str(cur_frame+1)].set_size(size = ld)
            if cur_frame == 15:
                cur_frame = 0
            else:
                cur_frame += 1
        elif event == "Nah. Scrap it.":
            break
        elif event == "Yep. Print please!":
            #implement send pdf to printer
            break
            
    gui_window.Close()












def print(fname):
    cmd = "lp " + fname
    print(cmd)
    os.system(cmd)

# print('/home/woojac/proj/019_photobooth_flipbook/test.pdf')