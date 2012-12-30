Application : pic_timeline.pyw
Support     : custom_dlgs.py
              constants.py
Third Party : EXIF.py
                Copyright (c) 2002-2007 Gene Cash All rights reserved
                Copyright (c) 2007-2012 Ianaré Sévi All rights reserved
              appdirs.py
                Copyright (c) 2005-2010 ActiveState Software Inc.        

Author       : Kyle Kawamura
Written with : Python 2.7.3
Tested on    : OSX 10.8 (Mountain Lion)
               Windows 7 x64
Objective    : A slightly useful application to mess around with while I learn
               Python. 
           
Backstory: Nowadays, everything is a camera.  When I get back from a trip I'll
have pictures from several digital cameras, digital version of film, and items
that are flatbed scanned.  Here's the problem: I like being able to look at the
photos in chronological order to relive my vacation glory but how can you do
that easily?  Sorting by modified time or EXIF metadata sounds good but that
assumes that all sources are time-synchronized.  Remember, phones and tablets
probably sync with local time zone, cameras don't...  scans have no correlation
to when the source was taken... and "what?  My sister's point and shoot camera
was set 45 minutes off?  Arggh!"

This application attempts to fix this by allowing you to specify multiple
sources of photos and optionally time-shift the source to account for any
discrepancies.  Once images are imported from these sources you can manually 
override individual photos with specific datetimes in case a mere time-shift
doesn't help (ex. scanned images or digital version of file).  You can preview
the proposed output order at any time.  On Mac, it uses the preview app which
is very convenient.  On Windows, the photos are copied to a temp folder so that
the app can specify the order which can then be assessed using PhotoViewer or
Windows Explorer.  No preview is available for Linux at the moment (I don't 
have access to a Linux box to test).  Once the order is okay, specify an output
file prefix (ex. "Honeymoon_") and the output directory and then go!  You now
have all your photos reordered sequentially according to filename.  The files
are not changed at all except for the name.

I must say, I find it pretty cool seeing my events/vacation activities, shown
from multiple angles, in real-time order.  :)

NOTES:
- EXIF 'Image DateTime' is used if found.  Otherwise file's modified-time.

HINTS:
 - If working with many photos and you need to override datetime values, use
   Finder/Explorer or other photo viewer to get an idea of the general area
   to move the photos to.  Move them to that general area and then fine-tune
   using "Preview" and tweak the override datetime.
 - Time shifting a source can be tricky to get right so consider it a work
   around.  Ideally, synchronize your cameras before the event!
 - Typically, photos that require extensive datetime overrides (scans, digital
   versions of film, etc) will be at the END of the list of photos (since
   they're most likely dated AFTER your event).  Use this trend to make sure
   all out of order photos are properly sequenced.
 - Previewing on Windows can be a little heavy-duty so I wouldn't preview
   hundreds of photos at a time...
