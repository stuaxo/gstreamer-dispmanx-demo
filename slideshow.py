#!/usr/bin/env python

"""
Slideshow to preview files.

Advances to next file every 3 seconds by default.

This is to demonstrate the kind of interrupted playback that
can happen in a networked client, without any networking :)


See the README for info which bugs you can reproduce with this.
"""

import ctypes
import argparse
import logging
import itertools
import os
import subprocess
import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstGL', '1.0')

from gi.repository import GObject, Gst, GstGL


def on_error(bus, msg):
    sys.exit(1)


def play_files(files, enable_bcm, loop=False, use_null=False, delay=3000, repeat=0):
    """
    :param files: files to play
    :param enable_bcm: if True then create a dispmanx (raspberry pi) window
    """
    global file_iter, play_count
    
    play_count = 0
    if loop or repeat:
        file_iter = itertools.cycle(files)  # loop over files forever
    else:
        file_iter = files.__iter__()

        
    Gst.init()
    mainloop = GObject.MainLoop()

    src = Gst.ElementFactory.make("filesrc", "src")
    src.set_property("location", os.path.abspath(files[0]))

    decode = Gst.ElementFactory.make("decodebin", "decode")
    sink = Gst.ElementFactory.make("glimagesink", "sink")

    def decode_src_created(element, pad):
        pad.link(sink.get_static_pad('sink'))

    decode.connect('pad-added', decode_src_created)

    pipeline = Gst.Pipeline()
    pipeline.add(src)
    pipeline.add(decode)
    pipeline.add(sink)

    src.link(decode)

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect('message::error', on_error)

    if enable_bcm:
        # Raspberry pi:  Create a dispmanx element for gstreamer to render to and pass it to gstreamer
        import bcm

        width, height = bcm.get_resolution()

        # Create a window slightly smaller than fullscreen
        nativewindow = bcm.create_native_window(50, 50, width -100, height-100, alpha_opacity=0)
        win_handle = ctypes.addressof(nativewindow)

        def on_sync_message(bus, msg):
            if msg.get_structure().get_name() == 'prepare-window-handle':
                _sink = msg.src
                _sink.set_window_handle(win_handle)  # Needs recent Gstreamer
                _sink.set_render_rectangle(0, 0, nativewindow.width, nativewindow.height)

        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', on_sync_message)
    else:
        nativewindow, win_handle = None, None

    def play_next_file(*args, **kwargs):
        global file_iter, play_count
        subprocess.run("sudo vcdbg reloc | grep free", shell=True)
        try:
            fn =  os.path.abspath(next(file_iter))
        except StopIteration:
            print("Bye.")
            sys.exit(0)
        
        print("%s: play %s #%s" % (__file__, fn, play_count))
        if use_null:
            # BUG 776091: with --enable-bcm the window will be destroyed, so you need to set to NULL to get a new one
            pipeline.set_state(Gst.State.NULL)
        else:
            pipeline.set_state(Gst.State.READY)
        pipeline.get_state(Gst.CLOCK_TIME_NONE)
        
        src.set_property('location', fn)
        pipeline.set_state(Gst.State.PLAYING)
        play_count += 1
        
        if repeat and play_count > repeat:
            sys.exit(0)
            return False
        return True


    play_next_file()
    GObject.timeout_add(delay, play_next_file, None)  # BUG 2: If this is set to a small value (250) the screen will go black after the first few files

    #running the playbin 
    pipeline.set_state(Gst.State.PLAYING)
    mainloop.run()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--enable-bcm', action='store_true', dest='enable_bcm', help="Enable BCM and set_window_handle")
    parser.add_argument('--use-null', action='store_true', dest='use_null', help="Enable BCM and set_window_handle")
    parser.add_argument('--loop', action='store_true', dest='loop', help="Loop playback")
    parser.add_argument('--repeat', default=0, dest='repeat', help="Repeat playback N times.", type=int)
    parser.add_argument('--delay', default=3000, dest='delay', help="Delay before advancing", type=int)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        sys.exit()

    play_files(**vars(args))


if __name__=="__main__":
    main()
