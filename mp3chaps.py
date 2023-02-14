#!/usr/bin/env python
# encoding: utf-8
"""
Usage:
  mp3chaps.py -h
  mp3chaps.py (-i | -r | -l | -p | -e=<fmt> | -t) <filename>

Options:
  -h       Show this help text
  -i       Import chapters from <filename>.chapters.txt
  -r       Remove chapters from <filename>
  -l       List chapters in <filename>
  -p       List chapters with frame details in <filename>
  -e=<fmt> Export chapters to <filename>.[chaps.txt | cue]
           fmt=(tc|ms|cue) (timecode | milliseconds | cue sheet)
  -t       Add test chapters from <filename>

"""

import eyed3
from docopt import docopt
import os


def list_chaps(tag):
    """list chapters in tag"""
    print("Chapters List:")
    for toc in tag.table_of_contents:
        for chap_id in toc.child_ids:
            chapter = tag.chapters[chap_id]
            print("{} {}".format(to_timecode(chapter.times[0]), chapter.title))


def remove_chaps(tag):
    """remove all the chapters and save tag to file"""
    for toc in tag.table_of_contents:
        for chap_id in toc.child_ids:
            print("removing {}".format(tag.chapters[chap_id].title))
            tag.chapters.remove(chap_id)
        tag.table_of_contents.remove(toc.element_id)
    tag.save()


def parse_chapters_file(fname):
    """Read and decode lines from input file"""
    filename, ext = os.path.splitext(fname)
    chapters_fname = "{}.chapters.txt".format(filename)
    chaps = []
    with open(chapters_fname, "r", encoding="utf-8-sig") as f:
        for line in f.readlines():
            if '\t' in line:
                #audacity
                time, title = line.split('\t')[0], line.split('\t')[2].strip()
                mstime = float(time) * 1000.0
            else:
                time, title = line.split()[0], " ".join(line.split()[1:])
                if time.count(':') == 2:
                    # timecode
                    mstime = float(to_millisecs(time))
                else:
                    # milliseconds
                    mstime = float(int(time))

            print(time, title)
            chaps.append((mstime, title))
    return chaps


def add_chapters(fi, fname):
    """Import chapter marks from text file"""
    tag = fi.tag
    tm = float(int(fi.info.time_secs * 1000.0))
    chaps = parse_chapters_file(fname)

    chapswk = []
    for i, chap in enumerate(chaps):
        if i < (len(chaps) - 1):
            chapswk.append(((chap[0], chaps[i + 1][0]), chap[1]))
    chapswk.append(((chaps[-1][0], tm), chaps[-1][1]))
    index = 0
    child_idsb = []

    for chap in chapswk:
        element_id = "ch{}".format(index).encode()
        times, title = chap
        tag.chapters.set(element_id, times)
        tag.chapters[element_id].title = u"{}".format(title)
        child_idsb.append(element_id)
        index += 1
    tag.table_of_contents.set(b"toc", toplevel=True, child_ids=child_idsb, description=u"Table of Contents")

    # list_chaps(tag)
    # print_chaps(tag)
    tag.save()


def print_chap(chapter):
    """List chapters with frame details"""
    print("= Chapter ID '%s'" % chapter.element_id)
    print("- Title:", chapter.title)
    print("- Start time: %d; End time: %d" % chapter.times)
    print("- Sub frames:", str(list(chapter.sub_frames.keys())))


def print_chaps(tag):
    for toc in tag.table_of_contents:
        print("toc ID:", toc.element_id)
        for chap_id in toc.child_ids:
            print_chap(tag.chapters[chap_id])


def write_chaps(tag, fname, fmt):
    """Export chapters to <filename>.<chaps.txt|cue> in specified format"""
    jname, jext = os.path.splitext(fname)
    if fmt == "=cue":
        chaps_fname = f"{jname}.cue"
        track = 0
    else:
        chaps_fname = f"{jname}.chaps.txt"
    print("Exporting: ", chaps_fname)
    print("Chapters List:")
    with open(chaps_fname, "w", encoding="utf-8-sig") as f:
        if fmt == "=cue":
            bn = os.path.basename(fname)
            f.write(f'FILE "{bn}" MP3\n')
        for toc in tag.table_of_contents:
            for chap_id in toc.child_ids:
                chapter = tag.chapters[chap_id]
                if fmt == "=cue":
                    track += 1
                    fmtstr = to_cuesheet(chapter.times[0])
                    f.write(f"TRACK {int(track):02d} AUDIO\n")
                    f.write(f'    TITLE "{chapter.title}"\n')
                    f.write(f"    INDEX 01 {fmtstr}\n")
                else:
                    print(chapter.times[0])
                    if fmt=="=ms":
                        sttime = "{:08d}".format(chapter.times[0])
                    else:
                        sttime = to_timecode(chapter.times[0])
                    line = "{} {}".format(sttime, chapter.title)
                    print(line)
                    f.write("{}\n".format(line))


def to_millisecs(time):
    """from timestamp hh:mm:ss.mmm"""
    h, m, s = [float(x) for x in time.split(":")]

    return int(1000 * (s + m * 60 + h * 60 * 60))


def to_timecode(ms):
    """from milliseconds to timecode """
    ss = int(ms / 1000.0)
    nn = int(ms - (ss * 1000))
    mm = int(ss / 60.0)
    ss -= (mm * 60)
    hh = int(mm / 60.0)
    mm -= (hh * 60)

    return "{:02d}:{:02d}:{:02d}.{:03d}".format(hh,mm,ss,nn)


def to_cuesheet(ms):
    """from milliseconds to cuesheet track"""
    ss, nn = divmod(ms, 1000)
    mm, ss = divmod(ss, 60)
    fr = round(int(nn) * 0.075)

    return "{:02d}:{:02d}:{:02d}".format(int(mm),int(ss),int(fr))


def test_chaps(tag):
    """Add test chapters marks"""
    # set chapters element_id, time(start, end)
    tag.chapters.set(b"chp1", (0.0, 10000.0))
    # title for chapter
    tag.chapters[b"chp1"].title = u"Chapter 1"

    tag.chapters.set(b"chp2", (10000.0, 20000.0))
    chapfrm = tag.chapters[b"chp2"]
    chapfrm.title = u"Chapter 2"

    tag.chapters.set(b"chp3", (20000.0, 30000.0))
    chapfrm = tag.chapters[b"chp3"]
    chapfrm.title = "Chapter 3"

    # add chapters to the toc
    tag.table_of_contents.set(
         b"toc", toplevel=True, child_ids=[b"chp1", b"chp2", b"chp3"],description=u"Table of Contents"
    )

    # save tag
    tag.save()


def main():
    """Entry point"""
    args = docopt(__doc__, version="mp3chaps 0.5.2")
    mp3file = args["<filename>"]
    print("filename: ", mp3file)

    fi = eyed3.load(mp3file)
    tag = fi.tag

    if args["-i"]:
        add_chapters(fi, mp3file)
    elif args["-r"]:
        remove_chaps(tag)
    elif args["-l"]:
        list_chaps(tag)
    elif args["-p"]:
        print_chaps(tag)
    elif args["-e"]:
        write_chaps(tag, mp3file, args["-e"])
    elif args["-t"]:
        test_chaps(tag)


if __name__ == '__main__':
    main()
