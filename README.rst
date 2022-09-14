mp3chapters
===========

 Command line utility for adding chapter marks to mp3 files.

 Many podcast and audiobook apps on Android and iOS support chapter markers in mp3 files

 This uses the `eyeD3 <https://github.com/nicfit/eyeD3>`_ lib to read and write the chapters details

requirements
------------
 Python 3

installation
++++++++++++

 ``pip3 install .``

usage
+++++

 The chapter markers format should be in either::
 
 - Timecode: hours:minutes:seconds.milliseconds + space + chapter title
 - Milliseconds: milliseconds (whole) + space + chapter title
 - Audacity: seconds (floating point) + tab + seconds (no used) + tab + chapter title

Assuming you have a file named ``episode_42.mp3``, ``mp3chaps`` looks for a chapter marks file called ``episode_42.chapters.txt`` in the same directory::
 
 00:00:00.000 Introduction 
 00:02:00.000 Chapter Title 
 00:42:24.123 Chapter Title 
 
 00000000 Introduction 
 00060000 Chapter Title 
 00276123 Chapter Title 
 
 0.000000	0.000000	Introduction 
 85.180378	85.180378	Chapter Title 
 543.822379	543.822379	Chapter Title 

Add chapter marks
++++++++++++++++++
 
 Add (import) chapter marks from text file (if chapters already exist, remove first with the option -r) 
 
 ``mp3chaps -i episode_42.mp3``

Remove chapters
+++++++++++++++
 
 ``mp3chaps -r episode_42.mp3`` 

List chapters
+++++++++++++
 ``mp3chaps -l episode_42.mp3``

List chapters with frame details
++++++++++++++++++++++++++++++++
 
 ``mp3chaps -p episode_42.mp3`` 

Export chapters to <filename>.chaps.txt::
+++++++++++++++++++++++++++++++++++++++++
 with **timecode** markers 
 
 ``mp3chaps -e=tc episode_42.mp3``

 with **milliseconds** markers 
 
 ``mp3chaps -e=ms episode_42.mp3``

Add test chapters marks
+++++++++++++++++++++++
 ``mp3chaps -t episode_42.mp3``
