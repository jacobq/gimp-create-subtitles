#!/usr/bin/python

from gimpfu import *

def plugin_main(#output_folder,
                text_file, width=1920, height=1080, x=0, y=0, font="Courier New", font_size_px=48, font_color=(0,0,0), save_png=False, save_xcf=False, show=False):
    # FIXME: Allow a folder to be selected as an input parameter -- this is not only more convenient but should help make this less platform-specific
    #output_folder = "C:\\Users\\Jacob\\Desktop\\subtitles"
    #directory_separator = "\\"
    output_folder = "/home/jquant/subtitles"
    directory_separator = "/"
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
            # limit iterations for debugging
            if (line_number > 1):
                break
            
            # Generate subtitle image
            img = create_subtitle(line.strip(), width, height, x, y, font, font_size_px, font_color);

            # Show the image
            if (show):
                gimp.Display(img)
                gimp.displays_flush()

            filename_without_extension = "subtitle_" + str(line_number).zfill(len(str(number_of_lines)))
            if (save_xcf):
                xcf_file = filename_without_extension + ".xcf"
                gimp.pdb.gimp_xcf_save(0, img, img.active_layer, output_folder + directory_separator + xcf_file, xcf_file)
            if (save_png):
                merged_layer = gimp.pdb.gimp_image_merge_visible_layers(img, 0)
                png_file = filename_without_extension + ".png"
                gimp.pdb.file_png_save_defaults(img, merged_layer, output_folder + directory_separator + png_file, png_file)

            if (not(show)):
                gimp.pdb.gimp_image_delete(img)

            line_number += 1

                
def create_subtitle(text, width, height, x, y, font, font_size_px, font_color):
    #gimp.message("Got parameters:\n"
    #    + "text: " + text + "\n"
    #    + "width: " + str(width) + "\n"
    #    + "height: " + str(height) + "\n"
    #    + "x: " + str(x) + "\n"
    #    + "y: " + str(y) + "\n"
    #    + "font: " + font + "\n"
    #    + "font_size_px: " + str(font_size_px) + "\n"
    #    + "font_color: " + str(font_color)
    #    )
    # Note: if you use RGBA_IMAGE here it doesn't output any warnings, but it gets interpreted as GRAY
    # Due to confusing the GimpImageBaseType and GimpImageType enum types
    img = gimp.Image(width, height, RGB) 

    # Create the transparent background "Frame" layer and add it to the image
    background_layer = gimp.Layer(img, "Frame", width, height, RGBA_IMAGE, 100, NORMAL_MODE)
    gimp.pdb.gimp_image_insert_layer(img, background_layer, None, -1)


    # Create the text layer
    text_layer = gimp.pdb.gimp_text_fontname(img, None, float(x), float(y), text, -1, True, font_size_px, PIXELS, font)
    gimp.pdb.gimp_text_layer_resize(text_layer, width-x, height-y)
    gimp.pdb.gimp_text_layer_set_justification(text_layer, TEXT_JUSTIFY_CENTER)
    gimp.pdb.gimp_text_layer_set_color(text_layer, font_color)
    #gimp.pdb.gimp_image_insert_layer(img, text_layer, None, 1) # Seems to get added automatically so this isn't needed

    # Create outline in layer behind text
    outline_layer = gimp.Layer(img, "Outline", width, height, RGBA_IMAGE, 100, NORMAL_MODE)
    gimp.pdb.gimp_image_insert_layer(img, outline_layer, None, 1)
    
    # Create path/vectors from text and stroke it on outline layer
    vectors = gimp.pdb.gimp_vectors_new_from_text_layer(img, text_layer)
    gimp.pdb.gimp_image_insert_vectors(img, vectors, None, -1)
    gimp.pdb.gimp_edit_stroke_vectors(outline_layer, vectors)
    
    # Run "Drop Shadow" plugin/script
    gimp.pdb.script_fu_drop_shadow(img, text_layer, 5, 5, 10, (0,0,0), 100, False)
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
            (PF_COLOR, "font_color", "The color of the font", (255, 255, 255)),
            (PF_BOOL, "save_png", "Save generated images as PNG files", False),
            (PF_BOOL, "save_xcf", "Save generated images as XCF files", False),
            (PF_BOOL, "show_images", "Display the images and don't close them", False)
        ],
        [],
        plugin_main)

main()
