# Characterization Report

## Characterization

Characterized 7 cells from the cell_data/control/ folder.
The median fit parameter is 0.12803258342064278 with 1 beyond 0.15.
The outlier cells are:

- RP_TEST1_3_2022-10-01_11-04-26 with fit error 0.17714123634961965
It is suggested to retest, rerun, or remove these cells from the dataset.

## Clustering

The characterized cells form 3 clusters, with a median variance of [0. 0. 0.] for each dimension.
There are 0 clusters with a variance beyond 0.12.
There are 2 clusters with only 1 member.
These isolated clusters are:

- 0 containing cell ['RP_TEST1_3_2022-10-01_11-04-26'].
  - Centroid [0.6960000000000001, 2.660013437271118, 0.6503299768273497]
- 2 containing cell ['RP_control_8_27_22'].
  - Centroid [0.608, 2.2700045108795166, 0.7027865457407236]

Isolated clusters will not be used for final matching.

## Matching

The clusters generate 2 matches using the specified parameters.
The matches, ordered by match metric, are as follows:

- metric used `power_opt_0`
- rank 0 match
  - cells ['TESTLAMINATED_0_2022-10-01_13-59-53', 'TESTLAMINATED_1_2022-10-01_14-01-14']
  - resulted in a metric of 8.133632952690126
- rank 1 match
  - cells ['RP_TEST2_264_2022-10-01_11-09-22', 'laminated_control_cell_7_7_18_0_2022-09-17_00-05-15']
  - resulted in a metric of 5.8739962348938
