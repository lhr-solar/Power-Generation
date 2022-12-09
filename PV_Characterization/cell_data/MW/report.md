# Characterization Report

## Characterization

Characterized 11 cells from the cell_data/MW/ folder.
The median fit parameter is 0.24446142235691898 with 5 beyond 0.25.
The outlier cells are:

- MW_29_2022-09-17_01-52-12 with fit error 0.25721642244658793
- MW_28_2022-09-17_01-54-08 with fit error 0.3754687153767783
- MW_30_2022-09-17_01-48-54 with fit error 0.6472410825674523
- MW_66_2022-09-17_01-35-27 with fit error 0.5424859364156173
- MW_32_2022-09-17_01-43-19 with fit error 0.630364039218775
It is suggested to retest, rerun, or remove these cells from the dataset.

## Clustering

The characterized cells form 1 clusters, with a median variance of [4.01983471e-05 1.39262573e-03 2.63632622e-04] for each dimension.
There are 0 clusters with a variance beyond 0.15.
There are 0 clusters with only 1 member.

## Matching

The clusters generate 5 matches using the specified parameters.
The matches, ordered by match metric, are as follows:

- metric used `power_opt_0`
- rank 0 match
  - cells ['MW_29_2022-09-17_01-52-12', 'MW_57_2022-09-17_01-33-03']
  - resulted in a metric of 6.833188801765448
- rank 1 match
  - cells ['MW_34_2022-09-17_01-37-33', 'MW_31_2022-09-17_01-46-53']
  - resulted in a metric of 6.553672785758977
- rank 2 match
  - cells ['MW_28_2022-09-17_01-54-08', 'MW_30_2022-09-17_01-48-54']
  - resulted in a metric of 6.220890884399418
- rank 3 match
  - cells ['MW_33_2022-09-17_01-41-21', 'MW_18_2022-09-17_01-57-26']
  - resulted in a metric of 6.015686187744146
- rank 4 match
  - cells ['MW_24_2022-09-17_02-00-17', 'MW_32_2022-09-17_01-43-19']
  - resulted in a metric of 5.794311168670659
