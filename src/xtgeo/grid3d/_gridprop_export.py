"""GridProperty (not GridProperies) export functions"""

from __future__ import print_function, absolute_import

import xtgeo.cxtgeo.cxtgeo as _cxtgeo
from xtgeo.common import XTGeoDialog
import xtgeo.common.sys as xtgeosys
from xtgeo.grid3d import _gridprop_lowlevel

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)

XTGDEBUG = 0


def to_file(self, pfile, fformat="roff", name=None, append=False, dtype=None):
    """Export the grid property to file."""
    logger.debug("Export property to file %s", pfile)

    xtgeosys.check_folder(pfile, raiseerror=OSError)

    if "roff" in fformat:
        if name is None:
            name = self.name

        binary = True
        if "asc" in fformat:
            binary = False

        # for later usage
        append = False
        last = True

        export_roff(self, pfile, name, append=append, last=last, binary=binary)

    elif fformat == "grdecl":
        export_grdecl(self, pfile, name, append=append, binary=False, dtype=dtype)

    elif fformat == "bgrdecl":
        export_grdecl(self, pfile, name, append=append, binary=True, dtype=dtype)


# Export ascii or binary ROFF format


def export_roff(self, pfile, name, append=False, last=True, binary=True):

    logger.info("Export roff to %s", pfile)
    if self._isdiscrete:
        _export_roff_discrete(
            self, pfile, name, append=append, last=last, binary=binary
        )
    else:
        _export_roff_continuous(
            self, pfile, name, append=append, last=last, binary=binary
        )


def _export_roff_discrete(self, pfile, name, append=False, last=True, binary=True):

    carray = _gridprop_lowlevel.update_carray(self, undef=-999)

    ptr_idum = _cxtgeo.new_intpointer()
    ptr_ddum = _cxtgeo.new_doublepointer()

    # codes:
    ptr_codes = _cxtgeo.new_intarray(256)
    ncodes = self.ncodes
    codenames = ""
    logger.info("Keys: %s", self.codes.keys())
    for inum, ckey in enumerate(sorted(self.codes.keys())):
        if ckey is not None:
            codenames += str(self.codes[ckey])
            codenames += "|"
            _cxtgeo.intarray_setitem(ptr_codes, inum, int(ckey))
        else:
            logger.warning("For some odd reason, None is a key. Check!")

    mode = 0
    if not binary:
        mode = 1

    if not append:
        _cxtgeo.grd3d_export_roff_pstart(
            mode, self._ncol, self._nrow, self._nlay, pfile, XTGDEBUG
        )

    nsub = 0
    isub_to_export = 0
    _cxtgeo.grd3d_export_roff_prop(
        mode,
        self._ncol,
        self._nrow,
        self._nlay,
        nsub,
        isub_to_export,
        ptr_idum,
        name,
        "int",
        carray,
        ptr_ddum,
        ncodes,
        codenames,
        ptr_codes,
        pfile,
        XTGDEBUG,
    )

    if last:
        _cxtgeo.grd3d_export_roff_end(mode, pfile, XTGDEBUG)

    _gridprop_lowlevel.delete_carray(self, carray)


def _export_roff_continuous(self, pfile, name, append=False, last=True, binary=True):

    carray = _gridprop_lowlevel.update_carray(self, undef=-999.0)

    ptr_idum = _cxtgeo.new_intpointer()

    mode = 0
    if not binary:
        mode = 1

    if not append:
        _cxtgeo.grd3d_export_roff_pstart(
            mode, self._ncol, self._nrow, self._nlay, pfile, XTGDEBUG
        )

    # now the actual data
    nsub = 0
    isub_to_export = 0

    _cxtgeo.grd3d_export_roff_prop(
        mode,
        self._ncol,
        self._nrow,
        self._nlay,
        nsub,
        isub_to_export,
        ptr_idum,
        name,
        "double",
        ptr_idum,
        carray,
        0,
        "",
        ptr_idum,
        pfile,
        XTGDEBUG,
    )

    if last:
        _cxtgeo.grd3d_export_roff_end(mode, pfile, XTGDEBUG)

    _gridprop_lowlevel.delete_carray(self, carray)


# Export ascii or binary GRDECL


def export_grdecl(self, pfile, name, append=False, binary=False, dtype=None):

    logger.info("Exporting %s to file %s, GRDECL format", name, pfile)

    if dtype is None:
        if self._isdiscrete:
            dtype = "int32"
        else:
            dtype = "float32"

    carray = _gridprop_lowlevel.update_carray(self, dtype=dtype)

    iarr = _cxtgeo.new_intpointer()
    farr = _cxtgeo.new_floatpointer()
    darr = _cxtgeo.new_doublepointer()

    if "double" in str(carray):
        ptype = 3
        darr = carray

    elif "float" in str(carray):
        ptype = 2
        farr = carray

    else:
        ptype = 1
        iarr = carray

    mode = 0
    if not binary:
        mode = 1

    appendmode = 0
    if append:
        appendmode = 1

    _cxtgeo.grd3d_export_grdeclprop2(
        self._ncol,
        self._nrow,
        self._nlay,
        ptype,
        iarr,
        farr,
        darr,
        self.name,
        pfile,
        mode,
        appendmode,
        XTGDEBUG,
    )

    _gridprop_lowlevel.delete_carray(self, carray)
