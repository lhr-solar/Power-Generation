# NOTE

> Pytables does not currently (11/24/2022) support python 3.11. This is required
> for accessing hdf files generated from pandas in nonideal_cell.py.
>
> For now, the c nonideal_model will be generated in 3.11 using cython for
> downstream characterization scripts.