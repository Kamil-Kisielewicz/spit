""" Module for tables of the Auto Typing paper
"""

# Imports
from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import glob, os, sys
import warnings
import pdb

from pkg_resources import resource_filename

from astropy import units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord, match_coordinates_sky

from linetools import utils as ltu

vik_path = '/scratch/citrisdance_viktor/viktor_astroimage/'

# Local
#sys.path.append(os.path.abspath("../Analysis/py"))
#sys.path.append(os.path.abspath("../Vetting/py"))
#from vette_dr7 import load_ml_dr7


# Summary table of DR7 DLAs
def mktab_training(outfil='tab_training.tex', sub=False):

    # Scan training images
    train_folder = vik_path + 'orig_images/'
    classes = glob.glob(train_folder + '/*')

    all_images = {}
    for iclass in classes:
        # Use rotated to get only one file per input image
        key = os.path.basename(iclass)
        all_images[key] = glob.glob(iclass + '/*_rotated.png')

    # Open
    tbfil = open(outfil, 'w')

    # Header
    #tbfil.write('\\clearpage\n')
    tbfil.write('\\begin{table*}\n')
    tbfil.write('\\centering\n')
    tbfil.write('\\begin{minipage}{170mm} \n')
    tbfil.write('\\caption{SDSS DR7 DLA CANDIDATES$^a$\\label{tab:dr7}}\n')
    tbfil.write('\\begin{tabular}{lcccccccc}\n')
    tbfil.write('\\hline \n')
    #tbfil.write('\\rotate\n')
    #tbfil.write('\\tablewidth{0pc}\n')
    #tbfil.write('\\tabletypesize{\\small}\n')
    tbfil.write('RA & DEC & Plate & Fiber & \\zabs & \\nhi & Conf. & BAL$^b$ \n')
    tbfil.write('& Previous?$^c$')
    tbfil.write('\\\\ \n')
    #tbfil.write('& & & (\AA) & (10$^{-15}$) & & (10$^{-17}$) &  ')
    #tbfil.write('} \n')
    tbfil.write('\\hline \n')

    #tbfil.write('\\startdata \n')

    bals, N09 = [], []
    cnt = 0
    for ii,dla in enumerate(ml_dlasurvey._abs_sys):
        if dla.zabs > dla.zem: # RESTRICTING
            N09.append(0)  # Make believe, but that is ok
            bals.append(0)
            continue
        if sub and (cnt > 5):
            break
        else:
            cnt += 1

        # Match to shen
        mt_shen = np.where( (shen['PLATE'] == dla.plate) & (shen['FIBER'] == dla.fiber))[0]
        if len(mt_shen) != 1:
            pdb.set_trace()
        # Generate line
        dlac = '{:0.4f} & {:0.4f} & {:d} & {:d} & {:0.3f} & {:0.2f} & {:0.2f} & {:d}'.format(
            ra[ii], dec[ii],
            dla.plate, dla.fiber, dla.zabs, dla.NHI, dla.confidence, shen['BAL_FLAG'][mt_shen[0]])
        bals.append(shen['BAL_FLAG'][mt_shen[0]])
        # In previous survey?
        flg_prev = 0
        if ml_in_pn[ii]:
            flg_prev += 1
            N09.append(1)
        else:
            N09.append(0)
        if in_dr5[ii]:
            flg_prev += 2
        dlac += '& {:d}'.format(flg_prev)
        # End line
        tbfil.write(dlac)
        tbfil.write('\\\\ \n')

    # End Table
    tbfil.write('\\hline \n')
    tbfil.write('\\end{tabular} \n')
    tbfil.write('\\end{minipage} \n')
    tbfil.write('{$^a$}Restricted to systems with $\mzabs < \mzem$.\\\\ \n')
    tbfil.write('{$^b$}Quasar is reported to exhibit BAL features by \cite{shen11} (1=True).  We caution that additional BAL features exist in the purported non-BAL quasars.\\\\ \n')
    tbfil.write('{$^c$}DLA is new (0) or is also reported by N09 (1), PW09 (2), or both (3).\\\\ \n')
    tbfil.write('\\end{table*} \n')

    #tbfil.write('\\enddata \n')
    #tbfil.write('\\tablenotetext{a}{Flag describing the continuum method applied: 0=Analysis based only on Lyman series lines; 1=Linear fit; 2=Constant fit; 3=Continuum imposed by hand.}\n')
    #tbfil.write('\\tablecomments{Units for $C_0$ and $C_1$ are erg/s/cm$^2$/\\AA\ and erg/s/cm$^2$/\\AA$^2$ respecitvely.}\n')
    # End
    #tbfil.write('\\end{deluxetable*} \n')

    tbfil.close()
    print('Wrote {:s}'.format(outfil))

    if sub:
        return

    # Some stats for the paper
    gd_conf = ml_dlasurvey.confidence > 0.9
    gd_BAL = np.array(bals) == 0
    gd_z = ml_dlasurvey.zabs < ml_dlasurvey.zem
    new = (np.array(N09) == 0) & (~in_dr5)
    gd_zem = ml_dlasurvey.zem < 3.8
    gd_new = gd_BAL & gd_conf & new & gd_z

    new_dlas = Table()
    new_dlas['PLATE'] = ml_dlasurvey.plate[gd_new]
    new_dlas['FIBER'] = ml_dlasurvey.fiber[gd_new]
    new_dlas['zabs'] = ml_dlasurvey.zabs[gd_new]
    new_dlas['NHI'] =  ml_dlasurvey.NHI[gd_new]
    print("There are {:d} DR7 candidates.".format(ml_dlasurvey.nsys))
    print("There are {:d} DR7 candidates not in BAL with zabs<zem.".format(np.sum(gd_BAL&gd_z)))
    print("There are {:d} good DR7 candidates not in BAL.".format(np.sum(gd_BAL&gd_conf&gd_z)))
    print("There are {:d} good DR7 candidates not in N09, PW09 nor BAL".format(np.sum(gd_new)))
    print("There are {:d} good DR7 candidates not in N09, PW09 nor BAL and with zem<3.8".format(np.sum(gd_new & gd_zem)))

    # Write out
    new_dlas.write("new_DR7_DLAs.ascii", format='ascii.fixed_width', overwrite=True)
    pdb.set_trace()

# Summary table of DR12 DLAs
def mktab_dr12(outfil='tab_dr12_dlas.tex', sub=False):

    # Load DLA
    _, dr12_abs = load_ml_dr12()

    # Cut on DLA
    dlas = dr12_abs['NHI'] >= 20.3
    dr12_dla = dr12_abs[dlas]
    dr12_dla_coords = SkyCoord(ra=dr12_dla['RA'], dec=dr12_dla['DEC'], unit='deg')

    # Load Garnett Table 2 for BALs
    tbl2_garnett_file = os.getenv('HOME')+'/Projects/ML_DLA_results/garnett16/ascii_catalog/table2.dat'
    tbl2_garnett = Table.read(tbl2_garnett_file, format='cds')
    tbl2_garnett_coords = SkyCoord(ra=tbl2_garnett['RAdeg'], dec=tbl2_garnett['DEdeg'], unit='deg')

    # Match and fill BAL flag
    dr12_dla['flg_BAL'] = -1
    idx, d2d, d3d = match_coordinates_sky(dr12_dla_coords, tbl2_garnett_coords, nthneighbor=1)
    in_garnett_bal = d2d < 1*u.arcsec  # Check
    dr12_dla['flg_BAL'][in_garnett_bal] = tbl2_garnett['f_BAL'][idx[in_garnett_bal]]
    print("There are {:d} sightlines in DR12 at z>1.95".format(np.sum(tbl2_garnett['z_QSO']>1.95)))
    print("There are {:d} sightlines in DR12 at zem>2 without BALs".format(np.sum(
        (tbl2_garnett['f_BAL']==0) & (tbl2_garnett['z_QSO']>2.))))

    # Load Garnett
    g16_abs = load_garnett16()
    g16_dlas = g16_abs[g16_abs['log.NHI'] >= 20.3]

    # Match
    dr12_to_g16 = match_boss_catalogs(dr12_dla, g16_dlas)
    matched = dr12_to_g16 >= 0
    g16_idx = dr12_to_g16[matched]
    not_in_g16 = dr12_to_g16 < 0

    # Stats
    high_conf = dr12_dla['conf'] > 0.9
    not_bal = dr12_dla['flg_BAL'] == 0
    zlim = dr12_dla['zabs'] > 2.
    gd_zem = dr12_dla['zabs'] < dr12_dla['zem']
    print("There are {:d} high confidence DLAs in DR12, including BALs".format(np.sum(high_conf)))
    print("There are {:d} z>2 DLAs, zabs<zem in DR12 not in a BAL".format(np.sum(not_bal&zlim&gd_zem)))
    print("There are {:d} high confidence z>2 DLAs in DR12 not in a BAL".format(np.sum(high_conf&not_bal&zlim&gd_zem)))
    print("There are {:d} high quality DLAs not in G16".format(np.sum(high_conf&not_bal&zlim&not_in_g16&gd_zem)))
    ml_not_in_g16 = gd_zem&high_conf&not_bal&zlim&not_in_g16
    wrest_ml_not = (1+dr12_dla['zabs'][ml_not_in_g16])*1215.67 / (1+dr12_dla['zem'][ml_not_in_g16])
    below_lyb = wrest_ml_not < 1025.7
    #pdb.set_trace()

    # Open
    tbfil = open(outfil, 'w')
    # Header
    #tbfil.write('\\clearpage\n')
    tbfil.write('\\begin{table*}\n')
    tbfil.write('\\centering\n')
    tbfil.write('\\begin{minipage}{170mm} \n')
    tbfil.write('\\caption{BOSS DR12 DLA CANDIDATES$^a$\\label{tab:dr12}}\n')
    tbfil.write('\\begin{tabular}{lcccccccc}\n')
    tbfil.write('\\hline \n')
    #tbfil.write('\\rotate\n')
    #tbfil.write('\\tablewidth{0pc}\n')
    #tbfil.write('\\tabletypesize{\\small}\n')
    tbfil.write('RA & DEC & Plate & Fiber & \\zabs & \\nhi & Conf. & BAL$^b$ \n')
    tbfil.write('& G16$^c$?')
    tbfil.write('\\\\ \n')
    #tbfil.write('& & & (\AA) & (10$^{-15}$) & & (10$^{-17}$) &  ')
    #tbfil.write('} \n')
    tbfil.write('\\hline \n')

    #tbfil.write('\\startdata \n')

    cnt = 0
    for ii,dla in enumerate(dr12_dla):
        if dla['zabs'] < 2.: # RESTRICTING
            continue
        if dla['zabs'] > dla['zem']: # RESTRICTING
            continue
        if sub and (cnt > 5):
            break
        else:
            cnt += 1
        # Generate line
        dlac = '{:0.4f} & {:0.4f} & {:d} & {:d} & {:0.3f} & {:0.2f} & {:0.2f} & {:d}'.format(
            dla['RA'], dla['DEC'],
            dla['Plate'], dla['Fiber'], dla['zabs'], dla['NHI'], dla['conf'], dla['flg_BAL'])
        # G16
        if matched[ii]:
            dlac += '& 1'
        else:
            dlac += '& 0'
        # End line
        tbfil.write(dlac)
        tbfil.write('\\\\ \n')

    # End
    tbfil.write('\\hline \n')
    tbfil.write('\\end{tabular} \n')
    tbfil.write('\\end{minipage} \n')
    #tbfil.write('{$^a$}Rest-frame value.  Error is dominated by uncertainty in $n_e$.\\\\ \n')
    #tbfil.write('{$^b$}Assumes $\\nu=1$GHz, $n_e = 4 \\times 10^{-3} \\cm{-3}$, $z_{\\rm DLA} = 1$, $z_{\\rm source} = 2$.\\\\ \n')
    tbfil.write('{$^a$}Restricted to systems with $\mzabs < \mzem$ and $\mzabs > 2$.\\\\ \n')
    tbfil.write('{$^b$}Quasar is reported to exhibit BAL features by the BOSS survey.\\\\ \n')
    tbfil.write('{$^c$}DLA is new (0) or reported by G16 (1).\\\\ \n')
    tbfil.write('\\end{table*} \n')

    #tbfil.write('\\enddata \n')
    #tbfil.write('\\tablenotetext{a}{Flag describing the continuum method applied: 0=Analysis based only on Lyman series lines; 1=Linear fit; 2=Constant fit; 3=Continuum imposed by hand.}\n')
    #tbfil.write('\\tablecomments{Units for $C_0$ and $C_1$ are erg/s/cm$^2$/\\AA\ and erg/s/cm$^2$/\\AA$^2$ respecitvely.}\n')
    # End
    #tbfil.write('\\end{deluxetable*} \n')

    tbfil.close()
    print('Wrote {:s}'.format(outfil))

#### ########################## #########################
def main(flg_tab):

    if flg_tab == 'all':
        flg_tab = np.sum( np.array( [2**ii for ii in range(5)] ))
    else:
        flg_tab = int(flg_tab)

    # DR7 Table
    if flg_tab & (2**0):
        mktab_dr7(outfil='tab_dr7_dlas_sub.tex', sub=True)
        #mktab_dr7()  # This one does the stats for the paper

    # DR12 Table
    if flg_tab & (2**1):
        mktab_dr12(outfil='tab_dr12_dlas_sub.tex', sub=True)
        #mktab_dr12()

# Command line execution
if __name__ == '__main__':

    if len(sys.argv) == 1:
        flg_tab = 0
        #flg_tab += 2**0   # DR7
        flg_tab += 2**1   # DR12
    else:
        flg_tab = sys.argv[1]

    main(flg_tab)
