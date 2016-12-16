Demoing some bugs in gstreamer on dispmanx (raspberry pi).


Bugs you can reproduce -


776166: On a Pi using --enable-bcm pipeline state has to be set to NULL to advance
       https://bugzilla.gnome.org/show_bug.cgi?id=776166

       instead of READY.   This means the screen flashes black.

       Doesn't work
       python-multi.py --enable-bcm rgba_pngs/*

       Works, but with black screen
       python-multi.py --enable-bcm --null-state rgba_pngs/*

776167: Advancing files too quickly seems to cause a black screen
       https://bugzilla.gnome.org/show_bug.cgi?id=776167

       python-multi.py --delay=250 rgba_pngs/*



776141: RGB pngs do not display: https://bugzilla.gnome.org/show_bug.cgi?id=776141

       python-multi.py rgb_pngs/*


776165: JPEGS do not display or display a glitched screen
       https://bugzilla.gnome.org/show_bug.cgi?id=776165

       python-multi.py jpegs/*


