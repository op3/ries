# This file is part of ries.

# ries is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ries is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ries.  If not, see <https://www.gnu.org/licenses/>.

r"""
Module for storing chemical-element data.

A chemical element with a symbol :math:`\mathrm{X}` is characterized by its proton number
:math:`\mathrm{Z}`.
It may consist of several different isotopes :math:`^A\mathrm{X}` with a mass number
:math:`\mathrm{A}` and an abundance :math:`x \left( ^A\mathrm{X} \right)`.
The (effective) mass number of the element :math:`A \left( \mathrm{X} \right)` is given by the weighted sum of all isotopic masses:

.. math:: A \left( \mathrm{X} \right) = \sum_A x \left( ^A\mathrm{X} \right) A

The `natural_elements` dictionary provides the data for all natural elements as given in a
compilation by Coursey et al. :cite:`Coursey2015`, plus the density data from Geant4 
:cite:`Agostinelli2003` :cite:`Allison2006` :cite:`Allison2016`.
The keys for the dictionary are the element symbols.
For example, to obtain the proton number of lead, type:

::

    from ries.constituents.element import natural_elements

    print(natural_elements['Pb'].Z)

For a detailed example of how to create a user-defined element, see `tests/boron.py`.

In addition, a dictionary called `X` is available which has the proton number as a key and the
element symbol as a value.
"""

from pathlib import Path

import numpy as np

from ries.constituents.natural_element_data import (
    Geant4DensityDataReader,
    NISTElementDataReader,
)


class Element:
    """Class representing a chemical element

    Attributes:

    - `Z`, int, proton number
    - `X`, str, element symbol
    - `isotopes`, array of `Isotope` objects, isotopes contained in the chemical element.
    - `abundances`, array of float, abundances of the isotopes.
      Must be at least as long as `isotopes`.
    - `amu`, float, effective mass of the element in atomic mass units (AMU).
    - `density`, float, density of the element in grams per cubic centimeter.
    """

    def __init__(self, Z, X, isotopes, abundances, density=None):
        """Initialization

        The initialization takes lists of isotopes and abundances and calculates the element mass.

        Parameters:

        - `Z`, int, proton number
        - `X`, str, element symbol
        - `isotopes`, array of `Isotope` objects, isotopes contained in the chemical element.
        - `abundances`, array of float, abundances of the isotopes.
          Must be at least as long as `isotopes`.
        - `density`, float, density of the element in grams per cubic centimeter (default: None).
        """
        self.Z = Z
        self.X = X
        self.isotopes = isotopes
        self.abundances = abundances
        self.density = density
        self.amu = self.amu_from_isotopic_composition(self.abundances, self.isotopes)

    @staticmethod
    def amu_from_isotopic_composition(abundances, isotopes):
        """Calculate element mass for a given isotopic composition

        Parameters:

        - `isotopes`, array of `Isotope` objects, isotopes contained in the chemical element.
        - `abundances`, array of float, abundances of the isotopes.
          Must be at least as long as `isotopes`.

        Returns:

        float, element mass
        """
        return np.sum([isotopes[iso].amu * abundances[iso] for iso in isotopes])


# Read the NIST natural elements data supplied with the `ries` repository and create the
# `natural_elements` dictionary.
geant4_density_data_reader = Geant4DensityDataReader(
    Path(__file__).parent.absolute() / "geant4_densities/element_densities.txt"
)
nist_element_data_reader = NISTElementDataReader(
    Path(__file__).parent.absolute() / "nist_elements/elements.txt"
)
X = nist_element_data_reader.read_nist_element_symbols()

natural_elements = {}
for Z in range(1, 119):
    abundances, isotopes = nist_element_data_reader.read_nist_element_data(Z)
    density = geant4_density_data_reader.read_density_data(X[Z])
    natural_elements[X[Z]] = Element(Z, X[Z], isotopes, abundances, density)
