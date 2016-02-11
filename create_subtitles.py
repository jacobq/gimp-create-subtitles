#!/usr/bin/python

from gimpfu import *

def plugin_main(output_folder, text_file, frame_width, frame_height,
                text_x, text_y,
                text_width, text_height,
                font, font_size_px, font_color,
                save_png, show_images,
                add_outline, outline_color, add_drop_shadow,
                generate_one_image_per_record,
                frame_rate,
                fade_time
                ):
    # TODO: Don't assume TSV data is sorted
    # FIXME: Make OS-agnostic, if possible/practical
    directory_separator = "\\"  # Windows
    #directory_separator = "/"  # POSIX
    
    
    def generate_subtitle_image():
        # Note: if you use RGBA_IMAGE here it doesn't output any warnings, but it gets interpreted as GRAY
        # Due to confusing the GimpImageBaseType and GimpImageType enum types
        img = gimp.Image(frame_width, frame_height, RGB) 

        # Create the transparent background "Frame" layer and add it to the image
        background_layer = gimp.Layer(img, "Frame", frame_width, frame_height, RGBA_IMAGE, 100, NORMAL_MODE)
        gimp.pdb.gimp_image_insert_layer(img, background_layer, None, -1)


        # Create the text layer
        text_layer = gimp.pdb.gimp_text_fontname(img, None, float(text_x), float(text_y), text, -1, True, font_size_px, PIXELS, font)
        gimp.pdb.gimp_text_layer_resize(text_layer, text_width, text_height)
        gimp.pdb.gimp_text_layer_set_justification(text_layer, TEXT_JUSTIFY_CENTER)
        gimp.pdb.gimp_text_layer_set_color(text_layer, font_color)
        #gimp.pdb.gimp_image_insert_layer(img, text_layer, None, 1) # Seems to get added automatically so this isn't needed

        # Create outline in layer behind text
        outline_layer = gimp.Layer(img, "Outline", frame_width, frame_height, RGBA_IMAGE, 100, NORMAL_MODE)
        gimp.pdb.gimp_image_insert_layer(img, outline_layer, None, 1)
        
        # Create path/vectors from text and stroke it on outline layer
        if (add_outline):
            vectors = gimp.pdb.gimp_vectors_new_from_text_layer(img, text_layer)
            gimp.pdb.gimp_image_insert_vectors(img, vectors, None, -1)
            # Save color before stroking then restore it back afterward
            prev_fg_color = gimp.get_foreground()
            gimp.set_foreground(outline_color)
            gimp.pdb.gimp_edit_stroke_vectors(outline_layer, vectors)
            gimp.set_foreground(prev_fg_color)
        
        # Run "Drop Shadow" plugin/script
        if (add_drop_shadow):
            gimp.pdb.script_fu_drop_shadow(img, text_layer, 5, 5, 10, (0,0,0), 100, False)

        return img
    
    def save_frame(img):
        # To work-around annoying loss-of-opacity-when-saving problem:
        # 1. Duplicate the main/merged layer and hide it
        # 2. Add a transparent layer at full opacity
        # 3. Merge visible layers
        #original_layer = img.active_layer
        #pdb.gimp_edit_copy(original_layer)
        #working_layer = gimp.Layer(img, "Working", frame_width, frame_height, RGBA_IMAGE, 100, NORMAL_MODE)
        #pdb.gimp_edit_paste(working_layer)
        
        #original_layer
        
        copy = gimp.pdb.gimp_layer_new_from_visible(img, img, "copy")
        gimp.pdb.gimp_image_insert_layer(img, copy, None, 1)
        
        #transparent_bg_layer = gimp.Layer(img, "Transparent BG", frame_width, frame_height, RGBA_IMAGE, 100, NORMAL_MODE)
        #gimp.pdb.gimp_image_insert_layer(img, transparent_bg_layer, None, 1)
        #merged_layer = gimp.pdb.gimp_image_merge_visible_layers(img, EXPAND_AS_NECESSARY)    
    
        filename_without_extension = "subtitle_" + str(current_frame).zfill(len(str(number_of_frames)))
        if (save_png):
            png_file = filename_without_extension + ".png"
            gimp.pdb.gimp_file_save(img, copy, output_folder + directory_separator + png_file, png_file)
        
        gimp.pdb.gimp_image_remove_layer(img, copy)
            
    # TODO: Support other easing functions besides linear
    def ease(in_min, in_current, in_max, out_start, out_end, type="linear"):
        progress = float((in_current - in_min)) / float((in_max - in_min))
        if (out_start > out_end):
            progress = 1 - progress
            temp = out_start
            out_start = out_end
            out_end = temp
        result = progress * (out_end - out_start) + out_start
        return float(result)

    with open(text_file) as f:
        current_frame = 1
        current_label = 1
        labels = f.readlines()
        number_of_labels = len(labels)
        number_of_frames = int(float(labels[-1].split("\t")[1]) * frame_rate)

        for label in labels:
            # Parse label row/line/record: file should be tab-delimited: (start, stop, text)
            [start, stop, text] = label.split("\t")
            start = float(start)
            stop = float(stop)
            text = text.decode('string_escape') # Allow \n to be interpreted as newline, etc.
            
            # Calculate keyframes for this label/record/cue
            start_frame = int(start * frame_rate)
            fade_in_end_frame = int((start + fade_time) * frame_rate)
            fade_out_start_frame = max(fade_in_end_frame, int((stop - fade_time) * frame_rate))
            end_frame = int(stop * frame_rate)
            
            # Generate the subtitle image
            img = generate_subtitle_image()
            merged_layer = gimp.pdb.gimp_image_merge_visible_layers(img, EXPAND_AS_NECESSARY)

            if (show_images):
                gimp.pdb.gimp_image_clean_all(img)
                gimp.Display(img)
                gimp.displays_flush()
            
            # Start as faded-out
            gimp.pdb.gimp_layer_set_opacity(merged_layer, 0)

            #DEBUG 
            #gimp.message(
            #      "start: " + str(start) + "\n"
            #    + "stop: " + str(stop) + "\n"
            #    + "text: " + text + "\n"
            #    + "start_frame: " + str(start_frame) + "\n"
            #    + "fade_in_end_frame: " + str(fade_in_end_frame) + "\n"
            #    + "fade_out_start_frame: " + str(fade_out_start_frame) + "\n"
            #    + "end_frame: " + str(end_frame) + "\n"
            #    )
                        
            # Seek first point where we fade this in
            while (current_frame < start_frame):
                # use last frame
                save_frame(img)
                current_frame += 1
            
            # Fade-in
            while (current_frame < fade_in_end_frame):
                opacity = ease(start_frame, current_frame, fade_in_end_frame, 0, 100)
                #gimp.message("opacity = " + str(opacity));
                gimp.pdb.gimp_layer_set_opacity(merged_layer, opacity)
                save_frame(img)
                current_frame += 1

            
            # Now we're faded-in
            gimp.pdb.gimp_layer_set_opacity(merged_layer, 100)

            
            # Seek fade-out start
            while (current_frame < fade_out_start_frame):
                save_frame(img)
                current_frame += 1
                
            # Fade-out
            while (current_frame < end_frame):
                opacity = ease(fade_out_start_frame, current_frame, end_frame, 100, 0)
                #gimp.message("opacity = " + str(opacity));
                gimp.pdb.gimp_layer_set_opacity(merged_layer, opacity)
                save_frame(img)
                current_frame += 1
            
            # Now we've faded out
            gimp.pdb.gimp_layer_set_opacity(merged_layer, 0)
            if (not(show_images)):
                gimp.pdb.gimp_image_delete(img)

            current_label += 1
            # limit iterations for debugging
            #if (current_label > 1):
            #    break
                
                   

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
            (PF_INT, "text_y", "The top-left Y coordinate to use for locating the text", 600),
            (PF_INT, "text_width", "The width of the text box", 1240),
            (PF_INT, "text_height", "The height of the text box", 154),
            (PF_FONT, "font", "The font to be used while generating the subtitles", "Segoe UI Bold"),
            (PF_INT, "font_size_px", "The size of the font (in px)", 40),
            (PF_COLOR, "font_color", "The color of the font", (255, 255, 255)),
            (PF_TOGGLE, "save_png", "Save generated images as PNG files", True),
            (PF_TOGGLE, "show_images", "Display the images and don't close them", False),
            (PF_TOGGLE, "add_outline", "Stroke the outline of the text", True),
            (PF_COLOR, "outline_color", "The color of the outline", (0, 0, 0)),
            (PF_TOGGLE, "add_drop_shadow", "Apply a drop shadow", True),
            #FIXME: re-implement this option (PF_TOGGLE, "generate_one_image_per_record", "Just generate one image file per record", True),
            (PF_TOGGLE, "generate_one_image_per_record", "Just generate one image file per record", False),
            (PF_FLOAT, "frame_rate", "Frames/second (used when generating time-aligned sequence)", 29.97),
            (PF_FLOAT, "fade_time", "Fade in/out time (seconds)", 0.300),
        ],
        [],
        plugin_main)

main()
