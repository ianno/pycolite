pycolite
====
#### a PYthon library for COntract-based design -- lite edition


This library provides a simple set of primitives to manipulate
*Linear Temporal Logic (LTL)-based Assume/Guarantee (A/G)contracts*.
It allows the definition of new contracts, compute compositions, and check for refinement, consistency,
and compatibility.

This library is used as a building block for a larger project:
[PyCo](https://github.com/ianno/pyco).

## Prerequisites
To use this library, you need to have [nuXmv](https://nuxmv.fbk.eu/) 1.1.1 installed on your system.

## Getting Started
This project can be installed as a python package,
and can be used by importing it in your python source files.

### Installing
To install the library, go to the root folder of the project and
modify setup.cfg to match your configuration.
Then, from a command line, run

```bash
pip install -e .
```

This last command will install all the required python dependencies.

### Testing
To make sure the installation has been successful,
you can run some tests by running from a command line,
always in the project root folder:

```bash
python -m pytest
```
After executing the last command, you should get a message saying that all the tests were passed.

### SCP 24
If you are looking for the code used for our SCP submission, you are looking for the code [in this branch](https://github.com/ianno/pycolite/tree/scp24) (or this [pre-release](https://github.com/ianno/pycolite/releases/tag/SCP24)). That branch contains the code used in the experimental section of the paper.
That code, however, is somewhat different than the rest of this repo, and some commands referenced in this README might not work.
This version requires nuXmv 1.1.1.

## Citations
Please **acknowledge** the use of pycolite by citing this Github repository and the article:

Iannopollo A., Tripakis S., Sangiovanni-Vincentelli A. (2017) Constrained Synthesis from Component Libraries. In: Kouchnarenko O., Khosravi R. (eds) Formal Aspects of Component Software. FACS 2016. Lecture Notes in Computer Science, vol 10231. Springer, Cham

or, in Bibtex format:

```bibtex
@Inbook{Iannopollo2017,
author="Iannopollo, Antonio
and Tripakis, Stavros
and Sangiovanni-Vincentelli, Alberto",
editor="Kouchnarenko, Olga
and Khosravi, Ramtin",
title="Constrained Synthesis from Component Libraries",
bookTitle="Formal Aspects of Component Software: 13th International Conference, FACS 2016, Besan{\c{c}}on, France, October 19-21, 2016, Revised Selected Papers",
year="2017",
publisher="Springer International Publishing",
address="Cham",
pages="92--110",
isbn="978-3-319-57666-4",
doi="10.1007/978-3-319-57666-4_7",
url="http://dx.doi.org/10.1007/978-3-319-57666-4_7"
}
```

Alternatively, you can cite this repo directly as:

[![DOI](https://zenodo.org/badge/95607363.svg)](https://zenodo.org/badge/latestdoi/95607363)

## Authors
* [Antonio Iannopollo](https://people.eecs.berkeley.edu/~antonio/)

## License
This project is released under the GPLv3 license.
For more information, see [LICENSE](https://github.com/ianno/pycolite/blob/master/LICENSE).
