from http.client import HTTPSConnection
from tkinter import filedialog as fd
from tkinterdnd2 import *
from threading import *
from tkinter import *
from json import *
from sys import *
from tkinter import ttk
from time import sleep
import tkinter as tk
import pyimgur
import random
import sys



'''
GUIDES I USED
https://www.quora.com/I-want-to-automatically-post-a-message-every-24-hours-on-my-Discord-server-using-my-own-account-not-a-bot-account-Is-this-possible-and-if-so-how   # STARTING POINT, REMOTE SENDER
https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/   # FILE DIALOG
https://pythonguides.com/python-tkinter-drag-and-drop/   # DRAG AND DROP FEATURE FOR MULTIPLE FILES
https://www.tutorialspoint.com/taking-input-from-the-user-in-tkinter   # ADDING INPUT ENTRY WIDGETS
https://www.youtube.com/watch?v=lvky-tmoTvg   # HOW TO USE IMGUR API, SIMPLE
https://www.delftstack.com/howto/python/python-replace-line-in-file/   # HOW TO REPLACE IMAGE PATHS ON DISK INTO POSTABLE IMGUR LINKS
https://www.geeksforgeeks.org/how-to-use-thread-in-tkinter-python/   # USEFUL EXAMPLE, SIMPLIFICATION OF THREADING
'''


'''↓↓↓↓ PROGRAM DOES NOT WORK WITHOUT!! ↓↓↓↓'''

TOKEN = ''   # FOR EX. OTM1MjUzMjI2MjY0MDY4MjM3.Ye7-rA.w3WsZ0DpCr4lKYurKPa_bLUodBQ
IMGUR_ID = ''    # FOR EX. 19a12e239az128h
CHANNEL_ID = ''    # FOR EX. 123821903821083257

'''↑↑↑↑ FOR PERSONAL USE: ONLY TOUCH THESE 3 SPECIFIERS ABOVE, TOKEN, IMGUR_ID, and CHANNEL_ID ↑↑↑↑'''

'''TOKEN is your discord token, BE CAUTIOUS ABOUT THIS USE. View the program below if you are unsure about it's usage.
IMGUR_ID is the API key that Imgur gives you once you sign up. Or you can use any image uploader service, discord will convert image links to images.
CHANNEL_ID is the ID of the discord channel (enabler developer view, copy ID of the text channel, assuming image perms)

Examples are FAKE/THROWAWAYS, use credible ID.
'''


global temporary_widget  # DO NOT TOUCH


class Client:
    '''
    Draws the GUI responsible for selecting image files to send to a discord channel.
    Notably a Drag and drop feature (can use multiple files but dragged one at a time)
    or through a file dialog.
    '''

    def __init__(self):
        self.main = TkinterDnD.Tk()
        self.main.title('Discord ImageBot')
        self.main.geometry('450x650')
        self.main.resizable(False, False)
        self.main.config(bg='#36393f')

        self.send_condition = tk.BooleanVar()
        self.send_condition.set(True)
        self.stop_condition = tk.BooleanVar()
        self.stop_condition.set(True)

        self.seconds_btwn_msg = 1  # an hour between sending each image by default
        self.seconds_before_stop = 360000

        self.image_paths = []
        self.temp_widget = Label()

        self._draw()
        self.main.mainloop()

    def _draw(self):
        global temporary_widget

        widget_text = 'Corbel 10 bold'

        # - - - - - - - - - - - - - - - - - - - - -
        # Open File System
        open_image_files = tk.Button(bg='#7289DA', fg='white', font='Corbel 12 bold', text='Open Image Files',
                command=self.select_files)
        open_image_files.pack(pady=10)

        OR = Label(anchor=CENTER, text='OR', bg='#36393f', fg='white', font=widget_text)
        OR.pack()

        drag_and_drop = Label(anchor=CENTER, text='Drag & Drop Images', bg='#36393f', fg='white',
                   font='Corbel 14 bold')
        drag_and_drop.pack()

        listbox = Listbox(width=45, height=15, bg='#36393f', fg='#FFFFFF', selectmode=EXTENDED)
        self.temp_widget = listbox
        listbox.pack()

        send_dropped_files = tk.Button(bg='#36393f', fg='white', font=widget_text, text='Send Dropped Files',
                command=self.threading)
        send_dropped_files.pack(pady=10)

        listbox.drop_target_register(DND_FILES)
        listbox.dnd_bind('<<Drop>>', self.add_to_listbox)

        # - - - - - - - - - - - - - - - - - - - - -
        # Connection Status bar
        frame = Frame(pady=20, padx=20)
        frame.config(bg='#36393f')
        frame.pack()

        separator = ttk.Separator(frame, orient=tk.HORIZONTAL)
        separator.grid(row=0, sticky='ew', pady=10, columnspan=10)

        # - - - - - - - - - - - - - - - - - - - - -
        # Time Interval Section
        interval_label = Label(frame, bg='#36393f', fg='white', font=widget_text, text='Time Between Message (min)')
        interval_label.grid(row=2, column=0)

        time_interval_entry = tk.Entry(frame, bg='#36393f', fg='white', font=widget_text)
        temporary_widget = time_interval_entry
        time_interval_entry.grid(row=2, column=1, columnspan=4, padx=10)

        update_button = tk.Button(frame, bg='#36393f', fg='white', font=widget_text, text='Update', command=self.set_interval)
        update_button.grid(row=2, column=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # Stop Later Section
        stop_later_label = Label(frame, bg='#36393f', fg='white', font=widget_text, text='Stop Later (min)')
        stop_later_label.grid(row=3, column=0)

        stop_later_entry = tk.Entry(frame, bg='#36393f', fg='white', font=widget_text)
        # temporary_widget = stop_later_entry  # doesnt work when you have multiple global carriers
        stop_later_entry.grid(row=3, column=1, columnspan=4, padx=10)

        update_button2 = tk.Button(frame, bg='#36393f', fg='white', font=widget_text, text='Update', command=self.later_interval)
        update_button2.grid(row=3, column=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # Stop Button
        stop_button = tk.Button(bg='#ce524d', fg='white', font=widget_text, text='Stop Sending', command=self.turn_off_sending)
        stop_button.pack()

        # - - - - - - - - - - - - - - - - - - - - -
        # Quit button
        quit_button = tk.Button(bg='#ce524d', fg='white', font=widget_text, text='Quit', command=self.quit)
        quit_button.pack(expand=True)

    def add_to_listbox(self, event):
        event.data = str(event.data).strip("{}[](),'")  # get rid of unusual symbols
        self.temp_widget.insert('end', event.data)  # inserts the event.data to be displayed in the Listbox
        self.image_paths.append(event.data)

    def select_files(self):
        '''
        The file dialog. Responsible for opening a file dialog window for the user so that you may select an image
        or multiple images to send to a discord channel.
        '''

        filetypes = (
            ('Image files', '*.png *.jpg *.jpeg *.tfif, *.tiff *.bmp *.gif *.eps *.raw'),
            ('All files', '*.*')
        )

        filepaths = fd.askopenfilenames(
        # opens the file dialog, also creates a tuple of the file paths
        # specified by options that are keyword arguments
            title='Open files',
            filetypes=filetypes)
        filepaths = list(filepaths)

        self.image_paths = filepaths

        self.threading()

    def write_to_file(self):
        '''
        Addresses obscure error with dragging 2 files, and then dragging in a previously dragged in file, resulting in an
        incorrectly formatted list, and makes sure that each image path gets its own individual line.
        '''

        ordered_image_paths = []

        for image_path in self.image_paths:
            elem = image_path.split()
            ordered_image_paths += elem

        self.image_paths = ordered_image_paths  # even if the list was initially correctly ordered,
        # it would still be set correctly (nothing changes)

        # ensure that one path gets one line
        with open('some_images.txt', 'w') as output:
            for image in self.image_paths:
                output.write(str(image) + '\n')

    def turn_off_sending(self):
        self.send_condition.set(False)

    def send_images(self):
        self.write_to_file()

        ImgurClient().imgur_convert()

        wp = WritePhrase()
        print('NEW RUN')
        print('-' * 20)

        while self.send_condition.get() and self.stop_condition.get():
            wp.sender('some_images.txt')  # this is the file we make

            if self.seconds_btwn_msg == '':
                print('why is this true')  # this happens when you have multiple objects assigned to the global temporary_widget
                self.seconds_btwn_msg = '1'
            min = int(self.seconds_btwn_msg) * 60
            print('min: ', min)
            sleep(min)

    def set_interval(self):
        if self.temp_widget != '':
            global temporary_widget
            self.seconds_btwn_msg = temporary_widget.get()
            print('min: ', self.seconds_btwn_msg)

    def later_interval(self):
        if self.temp_widget != '':
            global temporary_widget
            self.seconds_before_stop = temporary_widget.get()
            print(self.seconds_before_stop)

    def threading(self):
        t1 = Thread(target=self.send_images)  # simplest way to use a thread is to instantiate with a target function
        t1.start()  # and then call start

    def threading2(self):
        t2 = Thread(target=self.timed_loop)
        t2.start()

    def timed_loop(self):
        min = int(self.seconds_before_stop) * 60
        sleep(min)
        self.stop_condition.set(False)

    def quit(self):
        self.turn_off_sending()
        self.main.destroy()
        sys.exit(-1)  # defined in system, sys.exit()


class WritePhrase:
    '''
    Responsible for actually sending the message, in this case an imgur link to an image, to a specific discord channel.
    Given the discord user's token, the host (discordapp.com) and the ID of the discord channel (acts as a link)
    '''

    def __init__(self):
        self.used_phrases = []

    @staticmethod
    def get_connection():
        return HTTPSConnection('discordapp.com')  # similar to the smp_conn object we instantiated before
    # this HTTPSConnection object can be used to authenticate, read, write and return messages

    @staticmethod
    # static because its not bound to the object of the class, just sending
    def send_message(conn, channel_id, message_data):
        """
        request of HTTP takes method, url, body, and headers

        Get Channel Messages:
        /channels/{channel.id}/messages

        :param conn:
        :param channel_id:
        :param message_data:
        :return:
        """

        header_data = {
            'content-type': 'application/json',
            'authorization': TOKEN,
            'host': 'discordapp.com',
        }

        conn.request('POST', f'/api/v9/channels/{channel_id}/messages', message_data, header_data)
        resp = conn.getresponse()  # called after a request is sent to the server.
        # returns an HTTPResponse instance
        # you must read responses before sending new requests

        if 199 < resp.status < 300:
            print(f'Message {message_data} sent')
        else:
            stderr.write(f'Received HTTP {resp.status}: {resp.reason}\n')

    def sender(self, file):
        message = self.random_line(file)

        message_data = {
            'content': message,
            'tts': 'false',
        }

        self.send_message(self.get_connection(), CHANNEL_ID, dumps(message_data))

    def random_line(self, file_name) -> str:
        new_phrases = open(file_name).readlines()  # compute a list of lines WITH all the '\n' characters at the end

        if len(self.used_phrases) == len(new_phrases):
            self.used_phrases = []
            print()

        used_phrase = random.choice(new_phrases)
        while used_phrase in self.used_phrases:
            used_phrase = random.choice(new_phrases)

        self.used_phrases.append(used_phrase)

        return used_phrase


class ImgurClient:
    '''
    Client connects with Imgur, replaces the paths of selected images from file dialog or drag and drop and converts them
    to discord links so that they may be successfully posted on discord.
    '''

    @staticmethod
    def imgur_convert():
        file = open('some_images.txt', 'r')
        replacement = ''

        for image_path in file:
            image_path = image_path.strip()  # line must be stripped (removed of whitespaces AND line breaks) or its an invalid argument

            im = pyimgur.Imgur(IMGUR_ID)  # connect with Imgur
            image = im.upload_image(image_path)  # upload the image from its path

            change = image_path.replace(image_path, image.link) + '\n'  # replace the current line (image path)
            # with its created imgur link
            replacement += change  # updating replacement with the change

        file.close()
        # dividing it into reading then writing avoids confusion and errors
        fout = open('some_images.txt', 'w')  # resets the file, 'w' creates a new file if file opened already exists
        fout.write(replacement)  # because the write() method doesn't automatically add \n
        fout.close()


if __name__ == '__main__':
    Client()
