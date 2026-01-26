
# création de la fonction  'rasterisation'

from osgeo import gdal
import os

def rasterisation(in_vector, ref_image, out_image, field_name,
                  dtype="Int32", nodata=0, all_touched=True):

    # --- 1) Lecture des infos spatiales depuis l'image de référence ---
    ds = gdal.Open(ref_image)
    gt = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize

    # résolution (pixel size)
    res_x = gt[1]
    res_y = abs(gt[5])

    # emprise spatiale
    xmin = gt[0]
    ymax = gt[3]
    xmax = xmin + xsize * res_x
    ymin = ymax - ysize * res_y

    # --- 2) Options de GDAL ---
    touched_flag = "-at" if all_touched else ""
    nodata_opt = f"-a_nodata {nodata}" if nodata is not None else ""

    # --- 3) Construction la ligne de commande gdal ---
    cmd = (
        f"gdal_rasterize -a {field_name} "
        f"-tr {res_x} {res_y} "
        f"-te {xmin} {ymin} {xmax} {ymax} "
        f"-ot {dtype} -of GTiff {nodata_opt} {touched_flag} "
        f"{in_vector} {out_image}"
    )

    print("Commande exécutée :")
    print(cmd)

    # --- 4) Exécution ---
    os.system(cmd)
