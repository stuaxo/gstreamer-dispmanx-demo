Demoing some bugs in gstreamer on dispmanx (raspberry pi).


Bugs and how to reproduce them

776091: https://bugzilla.gnome.org/show_bug.cgi?id=776091

Background:

Usually, to play a file when another finishes you set the pipeline state
to READY, modify location on the src and then set state to PLAYING.

On Raspberry Pi with Dispmanx this doesn't work.

With the patch on bug 776091 you can set the state to NULL instead of READY,
however this is not ideal as the screen flashes black.

Reproduce:

Note - without the patch on 776091, neither of these will work:

Doesn't work
python-multi.py --enable-bcm rgba_pngs/*

Works, but with black screen
python-multi.py --enable-bcm --null-state rgba_pngs/*

Without the patch, if you play a video then it will freeze at the end.

776167: Advancing files too quickly seems to cause a black screen
       https://bugzilla.gnome.org/show_bug.cgi?id=776167

       python-multi.py --delay=250 rgba_pngs/*

776165: JPEGS do not display or display a glitched screen
       https://bugzilla.gnome.org/show_bug.cgi?id=776165

       python-multi.py jpegs/*


Fixed Bugs:

~~776141: RGB pngs do not display: https://bugzilla.gnome.org/show_bug.cgi?id=776141~~

~~python-multi.py rgb_pngs/*~~


