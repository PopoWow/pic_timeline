#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import tempfile
import shutil
from Tkinter import *
from tkFileDialog import askdirectory
from tkMessageBox import showerror
from datetime import datetime, timedelta
from time import strptime, mktime
from operator import attrgetter
import EXIF

from constants import *
from custom_dlgs import TimeShiftDialog, DateTimeDialog

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------        
APP_NAME = "Picture Timeliner"
MIN_WIDTH = 480
MIN_HEIGHT = 360
DEF_SIZE = "640x480"
COLS = 5
APP_GUID = "{75a56efb-b786-424f-b6a3-9649a5d22a83}"

# -----------------------------------------------------------------------------
# class TimeShiftDialog
#        Custom dialog that prompts for a timeshift value in seconds
# -----------------------------------------------------------------------------        
class PicTimelineApp(Frame):

    # -----------------------------------------------------------------------------
    # class SourceListData
    #        Data defining a source path
    # -----------------------------------------------------------------------------        
    class SourceListData(object):
        """Stores the time shift and color data for a source item."""
        
        colors = [{'fg':'red', 'bg':'white'}, {'fg':'green', 'bg':'white'},
                  {'fg':'blue', 'bg':'white'}, {'fg':'cyan', 'bg':'white'},
                  {'fg':'magenta', 'bg':'white'}, {'fg':'yellow', 'bg':'white'}]
        DEFAULT_COLORS = {'fg':'black', 'bg':'white'}
        
        def __init__(self):
            self.time_shift = 0
            
            # pop first item out of colors list and assign it to this source
            # if this source is deleted, then it's pushed back onto the list.
            # If no colors are left in the list, use the default of black on white. 
            self.color = (PicTimelineApp.SourceListData.colors.pop(0) 
                            if PicTimelineApp.SourceListData.colors 
                            else PicTimelineApp.SourceListData.DEFAULT_COLORS)
            
    # -----------------------------------------------------------------------------
    # class OutputsListData
    #        Data defining a file to be timelined
    # -----------------------------------------------------------------------------        
    class OutputsListData(object):
        """Stores the data for an file to process.
        id: Reference to a source item.  Can be used as key to sources dict.
        filename: Name of original image name to process
        data: Reference to source data object.  Used to get timeshift/color info.
        _dt: datetime information from file.  "dt" property can shift this
             with source's timeshift info (if any) or completely overriden
             by _dt_override.
        """
        def __init__(self, id, filename, data, dt):
            self.id = id
            self.filename = filename
            self.data = data
            
            # immutable datetime
            self._dt = dt
        
        # do this is str or repr?  str makes more sense. 
        def __str__(self):
            date_str = self.dt.strftime("%B %d, %H:%M:%S")
            return "{} ({})".format(self.filename, date_str)
        
        @property
        def colors(self):
            """Custom property getter that returns color on white (ex: red on white)
            if the item to process has not been overriden.  It flips to white on color
            if the ITEM has been manually overriden.
            """
            if self.is_overriden():
                retval = {'fg':self.data.color['bg'], 'bg':self.data.color['fg']}
                return retval
            else:
                return self.data.color
            
        @property 
        def dt(self):
            """dt property: returns original image file datetime.
            Can be modified with a source shift value or completely
            overriden by an Item override.
            """
            # property getter that returns the stored datetime value
            # shifted by the shift amount.
            if self.is_overriden():
                return self._dt_override
            else:
                # not overriden.  use original datetime with any shift value available
                retval = self._dt + timedelta(seconds=self.data.time_shift)
            return retval
        
        @dt.setter
        def dt(self, value):
            # the initial dt is immutable but can be overriden
            self._dt_override = value

        @dt.deleter
        def dt(self):
            """Delete process item override and revert to image file datetime + shift
            """
            # initial dt immutable
            if self.is_overriden():
                del self._dt_override
            
        # is this pythonic
        def is_overriden(self):
            return hasattr(self, "_dt_override")
        

    # -----------------------------------------------------------------------------
    # class PicTimelineApp members
    # -----------------------------------------------------------------------------        

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.sources_data = {}
        self.list_data = []
        
        # create our temp folder in the temp dir.  clear it out every session
        if sys.platform == "win32":
            # having problems launching the photoviewer for images staged in
            # %TEMP%.  Falling back to APPDATA...
            tempdir = os.environ['APPDATA']
        else:
            tempdir = tempfile.gettempdir()
            
        self.temp_dir = os.path.join(tempdir, 'KyleKawa', APP_GUID)

        if os.path.exists(self.temp_dir) and not os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        else:
            # get contents of temp_dir
            (dirpath, tmp_dirs, tmp_files) = next(os.walk(self.temp_dir))
            # delete files
            map(os.unlink, [os.path.join(dirpath, file) for file in tmp_files])
            # delete dirs
            map(shutil.rmtree, [os.path.join(dirpath, dir) for dir in tmp_dirs])
        
        # check file system case sensitivity
        # By default mkstemp() creates a file with a name that begins with 'tmp' (lowercase)
        # macos/windows do not seem to be case sensitive
        tmphandle, tmppath = tempfile.mkstemp(dir=self.temp_dir)
        self.fs_case_sensitive = not os.path.exists(tmppath.upper())
        try:
            print tmppath                                                           
            os.remove(tmppath)
        except:
            print 'Failed to remove tempfile: "{}"'.format(tmppath)
        
        self.configure_widgets()

    def configure_widgets(self):
        """definte and lay out tkinter widgets
        """        
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=ALL)
        
        self.rowconfigure(8, weight=1)

        for col in range(COLS):
            self.columnconfigure(col, weight=1)

        Label(self, text="Picture sources:").grid(row=0, column=0, columnspan=2, sticky=WIDTH)
        
        self.listbox_sources = Listbox(self, selectmode=SINGLE)
        self.listbox_sources.grid(row=1, column=0, columnspan=2, sticky=ALL)
        self.listbox_sources.bind("<Double-Button-1>", func=self.on_double_click_sources)
        
        Button(self, text="Add Source", command=self.handle_add_source).grid(row=2, column=0, sticky=WIDTH)
        Button(self, text="Delete Source", command=self.handle_delete_source).grid(row=2, column=1, sticky=WIDTH)
        
        Button(self, text="Set Output Path", command=self.handle_set_output_path).grid(row=3, column=0, columnspan=2, sticky=WIDTH)
        self.text_path = Text(self, width=20, height=2)
        self.text_path.grid(row=4, column=0, columnspan=2, sticky=WIDTH)
        
        Label(self, text="Set Output File Prefix:").grid(row=5, column=0, columnspan=2, sticky=WIDTH)
        self.file_prefix = Entry(self, width=20)
        self.file_prefix.grid(row=6, column=0, columnspan=2, sticky=WIDTH)
        
        Button(self, text="Go!", command=self.handle_do_the_thing).grid(row=7, column=0, columnspan=2, sticky=WIDTH)
        
        sub_frame = Frame(self, bg="red")
        sub_frame.rowconfigure(1, weight=1)
        sub_frame.columnconfigure(0, weight=1)
        sub_frame.grid(row=0, column=2, rowspan=9, columnspan=3, sticky=ALL)
        
        Label(sub_frame, text="Proposed Order").grid(row=0, column=0, sticky=WIDTH)
        self.listbox_output = Listbox(sub_frame, selectmode=EXTENDED)
        self.listbox_output.grid(row=1, column=0, sticky=ALL)
        self.listbox_output.bind("<Double-Button-1>", func=self.on_double_click_output)
        Button(sub_frame,
               text="Preview",
               command=self.handle_preview).grid(row=2, column=0, sticky=WIDTH)
    
    def get_source_key(self, ndx_sel):
        item_key = self.listbox_sources.get(ndx_sel)
        ndx_sep = item_key.find(":")
        if ndx_sep != -1:
            item_key = item_key[ndx_sep+1:]
        return item_key
    
    def handle_add_source(self):
        new_source_dir = askdirectory()
        
        if self.fs_case_sensitive:
            ok = new_source_dir not in self.listbox_sources.get(0, END)
        else:
            ok = new_source_dir.lower() not in [x.lower() for x in self.listbox_sources.get(0, END)]
        
        if ok:
            jpeg_files = [x for x in os.listdir(new_source_dir) if os.path.splitext(x)[1].lower() in [".jpg", ".jpeg"]]
            if jpeg_files:
                #directory is new(ok) and has some jpgs in it so add it
                self.listbox_sources.insert(END, new_source_dir)
                new_data = self.SourceListData()
                self.sources_data[new_source_dir] = new_data
                self.listbox_sources.itemconfig(END, new_data.color)
                
                self.process_new_source(new_source_dir, jpeg_files)

                self.listbox_sources.activate(END)
                self.listbox_sources.focus_set()
            else:
                showerror(title="Source selection error", message='"{}" does not contain any JPG images'.format(new_source_dir))
        else:
            showerror(title="Source selection error", message='"{}" already added as source'.format(new_source_dir))

    def handle_delete_source(self):
        cursel = self.listbox_sources.curselection()
        if cursel:
            index = int(cursel[0])
            key = self.get_source_key(index)
            
            # delete listbox item
            self.listbox_sources.delete(index)
            
            # restore the text color to the list of available colors unless it's
            # the default (black/white)
            cur_color = self.sources_data[key].color
            if (cur_color != PicTimelineApp.SourceListData.DEFAULT_COLORS):
                PicTimelineApp.SourceListData.colors.insert(0, cur_color)
            
            # delete item data corresponding to removed source
            del self.sources_data[key]
            #verify deletion
            print self.sources_data
            
            # update the outputs listbox and remove all files from the
            # deleted source
            self.list_data = [val for val in self.list_data if val.id != key]
            self.update_outputs()
        
    def on_double_click_sources(self, click_event):
        ndx_cursel = int(self.listbox_sources.curselection()[0])
        item_text = self.get_source_key(ndx_cursel)

        cur_data = self.sources_data[item_text]
        dlg = TimeShiftDialog(self, cur_data.time_shift)
        cur_data.time_shift = dlg.result 
        if dlg.result != None:
            if dlg.result != 0: # 0 is different from None!
                item_text = "{}:{}".format(dlg.result, item_text)        
        
            self.listbox_sources.insert(ndx_cursel, item_text)
            self.listbox_sources.itemconfig(ndx_cursel, cur_data.color)
            self.listbox_sources.delete(ndx_cursel+1)
            
            self.update_outputs()
            
    def on_double_click_output(self, click_event):
        ndx_cursel = int(self.listbox_output.curselection()[0])
        cur_item = self.list_data[ndx_cursel]
                
        dlg = DateTimeDialog(self, cur_item.dt, cur_item.is_overriden())
        if dlg.result:
            if dlg.result == "clear":
                del cur_item.dt
            else:
                cur_item.dt = dlg.result

            # try to be smart about the resort.  figure out where the
            # changed item will be moved and move it.  even if it doesn't
            # move, it needs to be redrawn.
            self.list_data.sort(key=attrgetter('dt'))
            ndx_sort = self.list_data.index(cur_item) # find out where item was moved
            if ndx_cursel != ndx_sort:
                # item was moved
                print "item moved from {} to {}".format(ndx_cursel, ndx_sort)
            else:
                print "item remains at {}".format(ndx_cursel)
                
            self.listbox_output.delete(ndx_cursel)
            self.listbox_output.insert(ndx_sort, cur_item)
            self.listbox_output.itemconfig(ndx_sort, cur_item.colors)

    def handle_set_output_path(self):
        new_source_dir = askdirectory()
        self.text_path.delete(1.0, END)
        self.text_path.insert(END, new_source_dir)
    
    def process_new_source(self, new_source_dir, jpeg_files):
        if not os.path.isdir(new_source_dir):
            # Should be able to get here but anyhoo
            raise ValueError("Input path is not a directory")
                        
        for file in jpeg_files:
            full_path = os.path.join(new_source_dir, file)
            with open(full_path, 'rb') as f:
                tags = EXIF.process_file(f)
                str_datetime = str(tags['Image DateTime'])
                if str_datetime:
                    ts = strptime(str_datetime, "%Y:%m:%d %H:%M:%S")
                    dt = datetime.fromtimestamp(mktime(ts))
                else:
                    dt = datetime.fromtimestamp(os.path.getmtime(full_path))
                
                new_item = self.OutputsListData(new_source_dir, file, self.sources_data[new_source_dir], dt)
                self.list_data.append(new_item)
        self.update_outputs()
        return True
        
    def update_outputs(self):
        self.list_data.sort(key=attrgetter('dt'))
        self.listbox_output.delete(0, END)
        for cur_item in self.list_data:
            self.listbox_output.insert(END, cur_item)
            self.listbox_output.itemconfig(END, cur_item.colors)
            
    def handle_do_the_thing(self):
        output_path = self.text_path.get(1.0, END).strip()
        prefix = self.file_prefix.get()
        if not output_path:
            showerror(title="Output path error", message='Enter a path for the output files')
            self.handle_set_output_path()
        elif not prefix:
            showerror(title="Output prefix error", message='Enter a prefix for the output files')
            self.file_prefix.focus_set()
        elif not self.list_data:
            showerror(title="No files to output", message='No files to process')
        else:
            # calculate how many digits needed to display all images
            index_width = len(str(len(self.list_data)))

            for ndx, src_path in enumerate([os.path.join(cur_item.id, cur_item.filename)
                                        for cur_item in self.list_data], 1):
                dest_path = os.path.join(output_path, "{}{}.jpg".format(prefix, str(ndx).zfill(index_width)))
                
                # use copy2 to preserve metadata
                shutil.copy2(src_path, dest_path)
                
                #print file, dest_path
    
    def handle_preview(self):
        # indexes come back as strs... d'oh!
        cursel = map(int, self.listbox_output.curselection())

        if sys.platform == "win32":
            # Windows photo viewer does not support opening list of pictures.
            # Open multiple instances in reverse order?
            files_to_preview = [os.path.normpath(os.path.join(self.list_data[index].id, self.list_data[index].filename))
                                for index in cursel]
#            
#            for file in files_to_preview:
#                cl_str = r'start rundll32.exe "%ProgramFiles%\Windows Photo Viewer\PhotoViewer.dll", ImageView_Fullscreen ' + file
#                print cl_str
#                os.system(cl_str)
#                from time import sleep
#                sleep(1) # sleep for 1 second to let photo viewer spin up.
#                         # otherwise windows might be out of order.

            # okay, i don't like that last approach.  Trying something else
            # copy preview files to a temp dir and point photo viewer to those.
            temp_subdir = tempfile.mkdtemp(dir=self.temp_dir)
            
            for (index, src_path) in [item for item in enumerate(files_to_preview, start=1)][::-1]:
                base, ext = os.path.splitext(src_path)
                base = os.path.basename(base)
                dest_path = os.path.join(temp_subdir, "{}({}){}".format(str(index).zfill(4), base, ext))
                shutil.copy2(src_path, dest_path)
            
            cl_str = r'start rundll32.exe "%ProgramFiles%\Windows Photo Viewer\PhotoViewer.dll", ImageView_Fullscreen '
            cl_str += dest_path
             
            os.system(cl_str)
                
        elif sys.platform == "darwin":
            # MAC
            files_to_preview = ["'{}'".format(os.path.join(self.list_data[index].id, self.list_data[index].filename)) for index in cursel]
            print files_to_preview
            cl_str = "open -a preview " + " ".join(files_to_preview)
            print cl_str            
            os.system(cl_str)
        elif sys.playform == "linux2":
            pass
        

root = Tk()
root.title(APP_NAME)
root.minsize(MIN_WIDTH, MIN_HEIGHT)
root.geometry(DEF_SIZE)
app = PicTimelineApp(master=root)
app.mainloop()
