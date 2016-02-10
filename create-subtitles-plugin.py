#!/usr/bin/python

from gimpfu import *

def plugin_main(#output_folder,
                text_file, width=1920, height=1080, x=0, y=0, font="Courier New", font_size_px=48, font_color=(0,0,0)):
    output_folder = "C:\\Users\\Jacob\\Desktop\\subtitles"
    #gimp.message("Got parameters:\n"
    #    + "output_folder: " + output_folder + "\n"
    #    + "text_file: " + text_file + "\n"
    #    + "width: " + str(width) + "\n"
    #    + "height: " + str(height) + "\n"
    #    + "x: " + str(x) + "\n"
    #    + "y: " + str(y) + "\n"
    #    + "font: " + font + "\n"
    #    + "font_size_px: " + str(font_size_px)
    #    )
    with open(text_file) as f:
        line_number = 1
        lines = f.readlines()
        number_of_lines = len(lines)
        for line in lines:
            # limit to 2 iterations for debugging
            if (line_number > 2):
                break
            
            img = create_subtitle(line.strip(), width, height, x, y, font, font_size_px, font_color);
            #layer = gimp.pdb.gimp_image_flatten(img) # strips alpha channel!
            filename_without_extension = "subtitle_" + str(line_number).zfill(len(str(number_of_lines)))
            png_file = filename_without_extension + ".png"
            xcf_file = filename_without_extension + ".xcf"
            gimp.pdb.file_png_save_defaults(img, img.active_layer, output_folder + "\\" + png_file, png_file)
            gimp.pdb.gimp_xcf_save(0, img, img.active_layer, output_folder + "\\" + xcf_file, xcf_file)
            line_number += 1
                
def create_subtitle(text, width, height, x, y, font, font_size_px, font_color):
    #gimp.message("Got parameters:\n"
    #    + "text: " + text + "\n"
    #    + "width: " + str(width) + "\n"
    #    + "height: " + str(height) + "\n"
    #    + "x: " + str(x) + "\n"
    #    + "y: " + str(y) + "\n"
    #    + "font: " + font + "\n"
    #    + "font_size_px: " + str(font_size_px)
    #    )
    img = gimp.Image(width, height, RGB_IMAGE)
    #layer = gimp.Layer(img, "Text", width, height, RGB_IMAGE, 100, NORMAL_MODE)
    gimp.pdb.gimp_palette_set_foreground(font_color);
    text_layer = gimp.pdb.gimp_text_fontname(img, None, float(x), float(y), text, -1, True, font_size_px, PIXELS, font)
    text_layer.add_alpha()
    return img
    

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
            # FIXME: PF_DIRNAME crashes on Windows??
            #(PF_DIRNAME, "output_folder", "Directory in which generates subtitle images will be placed", ""),
            (PF_FILE, "text_file", "A CRLF delimited text to be used for the subtitles", ""),
            (PF_INT, "frame_width", "The width of the images to be created", 1280),
            (PF_INT, "frame_height", "The height of the images to be created", 720),
            (PF_INT, "x_text", "The top-left X coordinate to use for locating the text", 0),
            (PF_INT, "y_text", "The top-left Y coordinate to use for locating the text", 566),
            (PF_FONT, "font", "The font to be used while generating the subtitles", "Segoe UI Bold"),
            (PF_INT, "font_size_px", "The size of the font (in px)", 48),
            (PF_COLOR, "font_color", "The color of the font", (255, 255, 255))
        ],
        [],
        plugin_main)

main()