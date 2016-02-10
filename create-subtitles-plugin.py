#!/usr/bin/python

from gimpfu import *

def plugin_main(text_file, width=1920, height=1080, x=0, y=0, font="Segoe UI Bold"):
    #gimp.message("Got parameters:\n"
    #    + "width: " + str(width) + "\n"
    #    + "height: " + str(height) + "\n"
    #    + "x: " + str(x) + "\n"
    #    + "y: " + str(y) + "\n"
    #    + "font: " + font
    #    )
    with open(text_file) as f:
        line_number = 1
        for line in f.readlines():
            # limit to 2 iterations for debugging
            if (line_number > 1):
                break
            create_subtitle(line, line_number);
            line_number += 1
                
def create_subtitle(text, number):
    #gimp.message(text + ", " + str(number))
    

register(
        "create_subtitles",
        "Uses each line of a given text file to create an image with a text layer, outline, and drop shadow.",
        "Uses each line of a given text file to create an image with a text layer, outline, and drop shadow.",
        "Jacob Quant",
        "Jacob Quant",
        "2016",
        "<Toolbox>/Tools/Create subtitles...",
        "",
        [
            (PF_FILE, "text_file", "A CRLF delimited text to be used for the subtitles", ""),
            (PF_INT, "frame_width", "The width of the images to be created", 1280),
            (PF_INT, "frame_height", "The height of the images to be created", 720),
            (PF_INT, "x_text", "The top-left X coordinate to use for locating the text", 0),
            (PF_INT, "y_text", "The top-left Y coordinate to use for locating the text", 566),
            (PF_FONT, "font", "The font to be used while generating the subtitles", "Segoe UI Bold")
            ],
        [],
        plugin_main)

main()