# coding: utf-8
from __future__ import division, absolute_import
from __future__ import print_function

import os
import pytest

from xtgeo.grid3d import Grid
from xtgeo.grid3d import GridProperty
from xtgeo.common import XTGeoDialog
import test_common.test_xtg as tsetup

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    raise SystemExit

td = xtg.tmpdir
testpath = xtg.testpath

# =============================================================================
# Do tests
# =============================================================================

emegfile = '../xtgeo-testdata/3dgrids/eme/1/emerald_hetero_grid.roff'
reekfile = '../xtgeo-testdata/3dgrids/reek/REEK.EGRID'
reekroot = '../xtgeo-testdata/3dgrids/reek/REEK'
brilfile = '../xtgeo-testdata/3dgrids/bri/B.GRID'
brilgrdecl = '../xtgeo-testdata/3dgrids/bri/b.grdecl'


def test_import_wrong():
    """Importing wrong fformat, etc"""

    with pytest.raises(ValueError) as e_info:
        logger.warning(e_info)
        g = Grid().from_file(emegfile, fformat='roffdum')
        tsetup.assert_equal(g.ncol, 70)


def test_import_guess():
    """Import with guessing fformat"""

    g = Grid().from_file(emegfile)

    tsetup.assert_equal(g.ncol, 70)


def test_roffbin_import0():
    """Import ROFF on the form Grid().from_file and Grid(..)"""

    g = Grid().from_file(emegfile, fformat='roff')

    assert isinstance(g, Grid)

    g = Grid(emegfile, fformat='roff')

    assert isinstance(g, Grid)


def test_roffbin_import1():
    """Test roff binary import case 1"""

    g = Grid()
    g.from_file(emegfile, fformat="roff")

    tsetup.assert_equal(g.ncol, 70, txt='Grid NCOL Emerald')
    tsetup.assert_equal(g.nlay, 46, txt='Grid NLAY Emerald')

    # extract ACTNUM parameter as a property instance (a GridProperty)
    act = g.get_actnum()

    # get dZ...
    dz = g.get_dz()

    logger.info('ACTNUM is {}'.format(act))
    logger.debug('DZ values are \n{}'.format(dz.values[888:999]))

    dzval = dz.values3d
    # get the value is cell 32 73 1 shall be 2.761
    mydz = float(dzval[31:32, 72:73, 0:1])
    tsetup.assert_almostequal(mydz, 2.761, 0.001, txt='Grid DZ Emerald')

    # get dX dY
    logger.info('Get dX dY')
    dx, dy = g.get_dxdy()

    mydx = float(dx.values3d[31:32, 72:73, 0:1])
    mydy = float(dy.values3d[31:32, 72:73, 0:1])

    tsetup.assert_almostequal(mydx, 118.51, 0.01, txt='Grid DX Emerald')
    tsetup.assert_almostequal(mydy, 141.21, 0.01, txt='Grid DY Emerald')

    # get X Y Z coordinates (as GridProperty objects) in one go
    logger.info('Get X Y Z...')
    x, y, z = g.get_xyz(names=['xxx', 'yyy', 'zzz'])

    logger.info('X is {}'.format(act))
    logger.debug('X values are \n{}'.format(x.values[888:999]))

    tsetup.assert_equal(x.name, 'xxx', txt='Name of X coord')
    x.name = 'Xerxes'

    logger.info('X name is now {}'.format(x.name))

    logger.info('Y is {}'.format(act))
    logger.debug('Y values are \n{}'.format(y.values[888:999]))

    # attach some properties to grid
    g.props = [x, y]

    logger.info(g.props)
    g.props = [z]

    logger.info(g.props)

    g.props.append(x)
    logger.info(g.propnames)

    # get the property of name Xerxes
    myx = g.get_prop_by_name('Xerxes')
    if myx is None:
        logger.info(myx)
    else:
        logger.info("Got nothing!")


def test_eclgrid_import1():
    """Eclipse GRID import."""

    g = Grid()
    logger.info("Import Eclipse GRID...")
    g.from_file(brilfile, fformat="grid")

    tsetup.assert_equal(g.ncol, 20, txt='Grid NCOL from Eclipse')
    tsetup.assert_equal(g.nrow, 15, txt='Grid NROW from Eclipse')


def test_eclgrid_import2():
    """Eclipse EGRID import."""
    g = Grid()
    logger.info("Import Eclipse GRID...")
    g.from_file(reekfile, fformat="egrid")

    tsetup.assert_equal(g.ncol, 40, txt='EGrid NX from Eclipse')
    tsetup.assert_equal(g.nrow, 64, txt='EGrid NY from Eclipse')
    tsetup.assert_equal(g.nactive, 35838, txt='EGrid NTOTAL from Eclipse')
    tsetup.assert_equal(g.ntotal, 35840, txt='EGrid NACTIVE from Eclipse')


def test_eclgrid_import3():
    """Eclipse GRDECL import and translate"""

    g = Grid(brilgrdecl, fformat="grdecl")

    mylist = g.get_geometrics()

    xori1 = mylist[0]

    # translate the coordinates
    g.translate_coordinates(translate=(100, 100, 10), flip=(1, 1, 1))

    mylist = g.get_geometrics()

    xori2 = mylist[0]

    # check if origin is translated 100m in X
    tsetup.assert_equal(xori1 + 100, xori2, txt='Translate X distance')

    g.to_file(os.path.join(td, 'g1_translate.roff'), fformat='roff_binary')


def test_geometrics_reek():
    """Import Reek and test geometrics"""

    g = Grid(reekfile, fformat='egrid')

    geom = g.get_geometrics(return_dict=True, cellcenter=False)

    for key, val in geom.items():
        logger.info('{} is {}'.format(key, val))

    # compared with RMS info:
    tsetup.assert_almostequal(geom['xmin'], 456510.6, 0.1, 'Xmin')
    tsetup.assert_almostequal(geom['ymax'], 5938935.5, 0.1, 'Ymax')

    # cellcenter True:
    geom = g.get_geometrics(return_dict=True, cellcenter=True)
    tsetup.assert_almostequal(geom['xmin'], 456620, 1, 'Xmin cell center')


def test_simple_io():
    """Test various import and export formats"""

    gg = Grid(reekfile, fformat='egrid')

    assert gg.nx == 40

    filex = os.path.join(td, 'grid_test_simple_io.roff')

    gg.to_file(filex)

    gg2 = Grid(filex, fformat='roff')

    assert gg2.nx == 40


def test_ecl_run():
    """Test import an eclrun with dates and export to roff after a diff"""

    dates = [19991201, 20030101]
    rprops = ['PRESSURE', 'SWAT']

    gg = Grid(reekroot, fformat='eclipserun', restartdates=dates,
              restartprops=rprops)

    # get the property object:
    pres1 = gg.get_prop_by_name('PRESSURE_20030101')
    tsetup.assert_almostequal(pres1.values.mean(), 308.45, 0.001)

    pres1.to_file(os.path.join(td, 'pres1.roff'))

    pres2 = gg.get_prop_by_name('PRESSURE_19991201')

    if isinstance(pres2, GridProperty):
        pass

    logger.debug(pres1.values)
    logger.debug(pres2.values)
    logger.debug(pres1)

    pres1.values = pres1.values - pres2.values
    logger.debug(pres1.values)
    logger.debug(pres1)
    avg = pres1.values.mean()
    # ok checked in RMS:
    tsetup.assert_almostequal(avg, -26.073, 0.001)

    pres1.to_file(os.path.join(td, 'pressurediff.roff'), name='PRESSUREDIFF')