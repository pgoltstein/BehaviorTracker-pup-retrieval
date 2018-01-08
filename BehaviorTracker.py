#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 6 2017

@author: pgoltstein
"""

########################################################################
### Imports

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import sys


########################################################################
### Global Variables

glob_frame_no = 0


########################################################################
### Global Functions

def load_video_frame(filename, frame):
    cap = cv2.VideoCapture(filename)
    cap.set(1,frame)
    ret, im = cap.read()
    vid_frame = im.mean(axis=2).astype(np.uint8)
    cap.release()
    return vid_frame

def load_video_from_file(filename, frame=None, binning2x2=False):
    # Open video file using cv2
    cap = cv2.VideoCapture(filename)

    # Get parameters
    meta_data = {}
    meta_data['orig_height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    meta_data['orig_width']  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    if binning2x2:
        meta_data['height']      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
        meta_data['width']       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
    else:
        meta_data['height']      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        meta_data['width']       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    meta_data['nframes']     = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    meta_data['fps']         = cap.get(cv2.CAP_PROP_FPS)

    print('Loading video file: {}'.format(filename))
    print('Using datatype np.uint8')
    print('Dimensions: {} x {} pixels, {} frames at {} frames/s'.format(
        meta_data['orig_height'], meta_data['orig_width'],
        meta_data['nframes'], meta_data['fps'] ))
    if binning2x2:
        print('Performing 2 x 2 spatial binning into {} x {} pixels'.format(
            meta_data['height'], meta_data['width'] ))

    # Load all frames
    if frame == None:
        print('Loading frame {:6d}'.format(0), end='', flush=True)
        vid_data = np.zeros( ( meta_data['height'], meta_data['width'],
                                meta_data['nframes'] ), dtype=np.uint8 )
        if binning2x2:
            for i in range(meta_data['nframes']):
                if i%100 == 0:
                    print((6*'\b')+'{:6d}'.format(i), end='', flush=True)
                    sys.stdout.flush()
                ret, im = cap.read()
                im = im.mean(axis=2)
                im = im[::2,:]+im[1::2,:]
                vid_data[:,:,i] = ((im[:,::2]+im[:,1::2])/4).astype(np.uint8)
        else:
            for i in range(meta_data['nframes']):
                if i%100 == 0:
                    print((6*'\b')+'{:6d}'.format(i), end='', flush=True)
                    sys.stdout.flush()
                ret, im = cap.read()
                vid_data[:,:,i] = im.mean(axis=2).astype(np.uint8)
    else:
        print('Loading frame {:6d}'.format(frame), end='', flush=True)
        cap.set(1,frame)
        ret, im = cap.read()
        if binning2x2:
            im = im.mean(axis=2)
            im = im[::2,:]+im[1::2,:]
            vid_data = ((im[:,::2]+im[:,1::2])/4).astype(np.uint8)
        else:
            vid_data = im.mean(axis=2).astype(np.uint8)

    print('\n')

    # Close file
    cap.release()
    return (vid_data,meta_data)


########################################################################
### MainWindow Class

class MainWindow():
    """Class that runs the main options window"""

    def __init__(self, main):
        self.main = main

        # variables
        self.zoom = 1
        self.int_adj = 2
        self.video_filename = ""

        # Create load and save buttons
        self.main.title("Behavior video tracker")
        self.button_load = tk.Button(self.main, text="Select video file",
            fg="black", command=self.select_video_file)
        self.button_load.pack()
        # self.button_set_template = tk.Button(self.main, text="Set template",
        #     fg="black", command=self.set_template)
        # self.button_set_template.pack()
        # self.button_check_tracking = tk.Button(self.main, text="Check tracking",
        #     fg="black", command=self.check_tracking)
        # self.button_check_tracking.pack()
        self.button_about = tk.Button(self.main,
            text="About", fg="blue", command=self.about)
        self.button_about.pack()
        self.button_quit = tk.Button(self.main,
            text="Quit", fg="red", command=quit)
        self.button_quit.pack()

        # Set main window position
        main.update()
        w_main = self.main.winfo_width()
        h_main = 400
        w_scr = self.main.winfo_screenwidth()
        h_scr = self.main.winfo_screenheight()
        x_main = int(w_scr*0.01)
        y_main = int(h_scr*0.1)
        main.geometry('{}x{}+{}+{}'.format(w_main, h_main, x_main, y_main))

        # start info window
        self.main_position = {'x': x_main+w_main, 'y': y_main}
        self.info_win = InfoWindow(self.main, self.main_position)

    def select_video_file(self):
        self.video_filename = filedialog.askopenfilename()
        self.info_win.update(self.video_filename)
        self.vid_win = VideoWindow(self.main, \
            self.main_position, self.video_filename, self.zoom, self.int_adj )

    # def set_template(self):
    #     self.template = TrackingTemplate(self.main, \
    #         self.video_filename, self.main_position, self.zoom, self.int_adj)
    #
    # def check_tracking(self):
    #     VideoWindow(self.main, self.main_position, self.video_filename, \
    #         self.zoom, self.int_adj, self.template.get_template() )

    def about(self):
        top = tk.Toplevel()
        top.title("About this application")
        msg = tk.Message(top, text="This is a gui for analyzing behavioral" +\
            " data of pup-retrieval experiments.")
        msg.pack()
        button = tk.Button(top, text="Alrighty", command=top.destroy)
        button.pack()


########################################################################
### InfoWindow Class

class InfoWindow():
    """Class that runs the info/status window"""

    def __init__(self, main, position):
        self.top = tk.Toplevel()
        self.top.title("Information")
        tk.Label(self.top, text="File: ", fg="black")
        self.label_video_filename = tk.Label(self.top,
            text="File", fg="black")
        self.label_video_filename.pack()

        # Set info window position
        self.top.update()
        w_scr = main.winfo_screenwidth()
        w_info = int(0.4*w_scr)
        h_info = self.top.winfo_height()
        x_info = int(position['x'])
        y_info = int(position['y']-h_info*2)
        self.top.geometry('{}x{}+{}+{}'.format(w_info, h_info, x_info, y_info))

    def update(self, video_filename):
        self.label_video_filename.config(text="File="+video_filename)


########################################################################
### VideoWindow Class

class VideoWindow():
    """Class that runs a video display window"""

    def __init__(self, main, position, vid_file_name, \
                            zoom, int_adj, template=None):
        self.zoom = zoom
        self.int_adj = int_adj
        self.top = tk.Toplevel()
        self.template = template

        # Load first frame to get meta_data
        self.vid_file_name = vid_file_name
        (arr,self.meta_data) = \
            load_video_from_file( self.vid_file_name, frame=0 )
        self.max_vid_frames = self.meta_data['nframes']

        # Create canvas for image
        self.canvas = tk.Canvas( self.top, width=int(self.meta_data['width']*self.zoom),
                                        height=int(self.meta_data['height']*self.zoom))
        self.canvas.pack()
        self.slider = tk.Scale( self.top, from_=0, to=self.max_vid_frames, \
            orient=tk.HORIZONTAL, command=self.slider_update,\
            length=self.meta_data['width']*self.zoom)
        self.slider.pack()

        # Display image on canvas for first time
        self.imgTk=ImageTk.PhotoImage(Image.fromarray(arr).resize(\
            (int(self.meta_data['width']*self.zoom), \
            int(self.meta_data['height']*self.zoom)) ))
        self.image_on_canvas = self.canvas.create_image(0, 0,
                                                anchor=tk.NW, image=self.imgTk)

        # Show image
        self.vid_update(frame_no=0)

        # Set video window position
        self.top.update()
        x_temp = int(position['x'])
        y_temp = int(position['y'])
        self.top.geometry('+{}+{}'.format(x_temp, y_temp))

    def slider_update(self,event):
        frame_no = self.slider.get()
        self.vid_update(frame_no=frame_no)

    def vid_update(self, frame_no=0):
        global glob_frame_no
        glob_frame_no = frame_no
        arr = load_video_frame( \
            self.vid_file_name, glob_frame_no )
        arr = arr.astype(np.float)
        if self.template is not None:
            arr = self.template.astype(np.float)-arr
        arr = arr * self.int_adj
        arr[arr<0] = 0
        arr[arr > 255] = 255
        arr = arr.astype(np.uint8)
        self.imgTk=ImageTk.PhotoImage(Image.fromarray(arr).resize(\
            (int(self.meta_data['width']*self.zoom), \
            int(self.meta_data['height']*self.zoom)) ))
        self.canvas.itemconfig(self.image_on_canvas, image=self.imgTk)


########################################################################
# Set up main window and start main loop

root = tk.Tk()
MainWindow(root)
root.mainloop()
