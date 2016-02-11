#!/usr/bin/python

from gimpfu import *

def plugin_main(output_folder, text_file, frame_width, frame_height,
                text_x, text_y,
                text_width, text_height,
                font, font_size_px, font_color,
                save_png, save_xcf, show_images,
                add_outline, outline_color, add_drop_shadow,
                generate_one_image_per_record, frame_rate,
                fade_time_sec
                ):
    # FIXME: Make OS-agnostic, if possible/practical
    directory_separator = "\\"  # Windows
    #directory_separator = "/"  # POSIX

    with open(text_file) as f:
        line_number = 1
        lines = f.readlines()
        number_of_lines = len(lines)
        for line in lines:
            # Parse line: file should be tab-delimited: (start, stop, text)
            [start, stop, text] = line.split("\t")
            text = text.strip();
        
            # limit iterations for debugging
            if (line_number > 2):
                break
            
            # Generate subtitle image
            img = create_subtitle(text, frame_width, frame_height, text_x, text_y, text_width, text_hegith, font, font_size_px, font_color);

            # Show the image
            if (show_images):
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

            if (not(show_images)):
                gimp.pdb.gimp_image_delete(img)

            line_number += 1

                
def create_subtitle(text, frame_width, frame_height, text_x, text_y, text_width, text_height, font, font_size_px, font_color):
    # Note: if you use RGBA_IMAGE here it doesn't output any warnings, but it gets interpreted as GRAY
    # Due to confusing the GimpImageBaseType and GimpImageType enum types
    img = gimp.Image(width, height, RGB) 

    # Create the transparent background "Frame" layer and add it to the image
    background_layer = gimp.Layer(img, "Frame", frame_width, frame_height, RGBA_IMAGE, 100, NORMAL_MODE)
    gimp.pdb.gimp_image_insert_layer(img, background_layer, None, -1)


    # Create the text layer
    text_layer = gimp.pdb.gimp_text_fontname(img, None, float(x), float(y), text, -1, True, font_size_px, PIXELS, font)
    gimp.pdb.gimp_text_layer_resize(text_layer, text_width, text_height)
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
        "Takes a tab-delimited set of records and uses them to generate a series of images containing the corresponding text. Outputs either a single image per record or a time-aligned sequence (assuming constant frame-rate) of many images.",
        "Uses each line of a given text file to create an image with a text layer, outline, and drop shadow.",
        "Jacob Quant",
        "Jacob Quant",
        "2016",
        "<Toolbox>/Tools/Create subtitles...",
        "",
        [
            (PF_DIRNAME, "output_folder", "Directory in which generates subtitle images will be placed", "C:\\"),
            (PF_FILE, "text_file", "A tab-delimited text file (start seconds, stop seconds, line of text) to be used for the subtitles", ""),
            (PF_INT, "frame_width", "The width of the images to be created", 1280),
            (PF_INT, "frame_height", "The height of the images to be created", 720),
            (PF_INT, "text_x", "The top-left X coordinate to use for locating the text", 20),
            (PF_INT, "text_y", "The top-left Y coordinate to use for locating the text", 566),
            (PF_INT, "text_width", "The width of the text box", 1240),
            (PF_INT, "text_height", "The height of the text box", 154),
            (PF_FONT, "font", "The font to be used while generating the subtitles", "Segoe UI Bold"),
            (PF_INT, "font_size_px", "The size of the font (in px)", 48),
            (PF_COLOR, "font_color", "The color of the font", (255, 255, 255)),
            (PF_TOGGLE, "save_png", "Save generated images as PNG files", False),
            (PF_TOGGLE, "save_xcf", "Save generated images as XCF files", False),
            (PF_TOGGLE, "show_images", "Display the images and don't close them", False),
            (PF_TOGGLE, "add_outline", "Stroke the outline of the text", True),
            (PF_COLOR, "outline_color", "The color of the outline", (0, 0, 0)),
            (PF_TOGGLE, "add_drop_shadow", "Apply a drop shadow", True),
            (PF_TOGGLE, "generate_one_image_per_record", "Just generate one image file per record", True),
            (PF_FLOAT, "frame_rate", "Frames/second (used when generating time-aligned sequence)", 29.97),
            (PF_FLOAT, "fade_time_sec", "Fade in/out time (seconds)", 0.300),
        ],
        [],
        plugin_main)

main()
