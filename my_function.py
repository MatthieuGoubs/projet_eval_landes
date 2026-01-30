
# création de la fonction  'rasterisation'

from osgeo import gdal
import os
import numpy as np
import matplotlib.pyplot as plt


def rasterisation(in_vector, ref_image, out_image, field_name,
                  dtype="Int32", nodata=0, all_touched=True):
    """
    Permet la rasterisation d'un fichier shp à partir d'une image de référence.
    """
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
    os.system(cmd
    )



def diagnostic_qualite_indices(dict_X, nom_indice, dates):
    """
    Analyse la présence de valeurs aberrantes (NaN, Inf, hors limites) 
    dans les données extraites par strate.
    """
    print(f"DIAGNOSTIC : {nom_indice}")
    print(f"{'Strate':<15} | {'Date':<12} | {'NaN (%)':<10} | {'Inf (%)':<10} | {'Hors-limite (%)'}")
    print("-" * 75)

    # On boucle sur chaque strate (clé du dictionnaire)
    for strate_id in sorted(dict_X.keys()):
        data_strate = dict_X[strate_id] # Matrice (pixels, dates)
        
        # On analyse chaque date (colonne de la matrice)
        for i, date in enumerate(dates):
            values = data_strate[:, i]
            total = values.size
            
            # Détection des anomalies
            n_nan = np.isnan(values).sum()
            n_inf = np.isinf(values).sum()
            # Pour le NDVI/ARI, les valeurs doivent être entre -1 et 1
            n_out = ((values < -1) | (values > 1)).sum() 
            
            if n_nan > 0 or n_inf > 0 or n_out > 0:
                pct_nan = (n_nan / total) * 100
                pct_inf = (n_inf / total) * 100
                pct_out = (n_out / total) * 100
                
                print(f"ID {strate_id:<12} | {date:<12} | {pct_nan:>8.2f}% | {pct_inf:>8.2f}% | {pct_out:>8.2f}%")
    
    print("-" * 75)
    print("Diagnostic terminé.")



def generer_graphique_temporel(dict_X, titre, nom_axe_y, dates, dossier_sauvegarde=None, nom_fichier="graphique.png"):
    """
    Génère un graphique temporel standardisé pour les indices spectraux.
    """
    # Configuration des légendes et des styles visuels par classe (Strate)
    noms_strates = {2: "Strate 2 (Herbe)", 3: "Strate 3 (Landes)", 4: "Strate 4 (Arbre)"}
    couleurs_strates = {2: 'tab:blue', 3: 'tab:orange', 4: 'tab:green'}
   
    # Initialisation de la figure Matplotlib
    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(dates))

    # Boucle de traitement par classe présente dans le dictionnaire de données
    for lab in sorted(dict_X.keys()):

        # Récupération des pixels de la strate (Matrice : pixels x dates)
        data = dict_X[lab]

        # Calcul des statistiques descriptives (on ignore les valeurs NaN)
        mean = np.nanmean(data, axis=0)
        std = np.nanstd(data, axis=0)
        
        # Récupération du style associé à la classe (ID -> Nom/Couleur)
        color = couleurs_strates.get(int(lab), 'black')
        label = noms_strates.get(int(lab), f"Strate {int(lab)}")
        
        # Tracé de la ligne moyenne avec marqueurs circulaires
        ax.plot(x, mean, '-o', label=label, color=color, linewidth=2.5, markersize=8)

        # Tracé de l'enveloppe de variabilité (Moyenne +/- 1 Écart-type)
        # L'alpha à 0.15 crée une zone semi-transparente pour la lisibilité
        ax.fill_between(x, mean - std, mean + std, color=color, alpha=0.15)

    # Habillage et mise en forme du graphique
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=30)
    ax.set_xlabel("Dates d'acquisition Sentinel-2", fontweight='bold')
    ax.set_ylabel(nom_axe_y, fontweight='bold')
    ax.set_title(titre, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    
    plt.tight_layout()
    
    # Exportation du fichier si un dossier est spécifié
    if dossier_sauvegarde:
        full_path = os.path.join(dossier_sauvegarde, nom_fichier)
        plt.savefig(full_path)
        print(f"Graphique sauvegardé avec succès : {full_path}")
    
    # Affichage final à l'écran
    plt.show()