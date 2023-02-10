# Characterization Report

## Characterization

Characterized 12 cells from the cell_data/MW/ folder.
The median fit parameter is 0.21780794942003284 with 6 beyond 0.2.
The outlier cells are:

- MW_28_2022-09-17_01-54-08 with fit error 0.3754687153767783
- MW_29_2022-09-17_01-52-12 with fit error 0.25409792234624784
- MW_30_2022-09-17_01-48-54 with fit error 0.5618090051209409
- MW_31_2022-09-17_01-46-53 with fit error 0.23828955125004533
- MW_32_2022-09-17_01-43-19 with fit error 0.5042204667658701
- MW_66_2022-09-17_01-35-27 with fit error 0.42479758479520024
It is suggested to retest, rerun, or remove these cells from the dataset.

## Clustering

The characterized cells form 2 clusters, with a median variance of [3.75537190e-05 1.23063484e-03 1.37933635e-04] for each dimension.
There are 0 clusters with a variance beyond 0.2.
There are 1 clusters with only 1 member.
These isolated clusters are:

- 0 containing cell ['MW_17_2022-09-17_02-05-24'].
  - Centroid [0.672, 2.4650089740753174, 0.7339886939479627]

Isolated clusters will not be used for final matching.

## Matching

The clusters generate 5 matches using the specified parameters.
The matches, ordered by match metric, are as follows:

- metric used `power_opt_0`
- rank 0 match
  - cells ['MW_30_2022-09-17_01-48-54', 'MW_31_2022-09-17_01-46-53']
  - resulted in a metric of 6.772113166809084
- rank 1 match
  - cells ['MW_34_2022-09-17_01-37-33', 'MW_57_2022-09-17_01-33-03']
  - resulted in a metric of 6.586523537635805
- rank 2 match
  - cells ['MW_29_2022-09-17_01-52-12', 'MW_32_2022-09-17_01-43-19']
  - resulted in a metric of 6.3346677732467676
- rank 3 match
  - cells ['MW_18_2022-09-17_01-57-26', 'MW_28_2022-09-17_01-54-08']
  - resulted in a metric of 6.198945429801943
- rank 4 match
  - cells ['MW_33_2022-09-17_01-41-21', 'MW_66_2022-09-17_01-35-27']
  - resulted in a metric of 5.953016756057741
