#

def rasterisation (my_folder, in_vector, ref_image, out_image, field_name, sptial_resolution, xmin, ymin, xmax, ymax): 
    my_folder = my_folder
    in_vector = in_vector
    ref_image = ref_image
    out_image = out_image
    field_name = field_name

    sptial_resolution = sptial_resolution
    xmin = xmin
    ymin = ymin
    xmax = xmax
    ymax = ymax
    
    cmd_pattern = ("gdal_rasterize -a {field_name} "
               "-tr {sptial_resolution} {sptial_resolution} "
               "-te {xmin} {ymin} {xmax} {ymax} -ot Byte -of GTiff "
               "{in_vector} {out_image}")

    cmd = cmd_pattern.format(in_vector=in_vector, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, out_image=out_image, field_name=field_name, sptial_resolution=sptial_resolution)

    # execute the command in the terminal 
    os.system(cmd)