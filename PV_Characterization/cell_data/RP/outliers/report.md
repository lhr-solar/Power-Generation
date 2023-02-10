# Characterization Report

## Characterization

Characterized 17 cells from the cell_data/RP/outliers/ folder.
The median fit parameter is 0.09190143250598555 with 2 beyond 0.2.
The outlier cells are:

- RP_199_2022-09-24_13-52-54 with fit error 5.357833583536635
- RP_90_2022-09-17_15-26-30 with fit error 54.48998350918367
It is suggested to retest, rerun, or remove these cells from the dataset.

## Clustering

The characterized cells form 6 clusters, with a median variance of [0. 0. 0.] for each dimension.
There are 0 clusters with a variance beyond 0.5.
There are 4 clusters with only 1 member.
These isolated clusters are:

- 0 containing cell ['RP_199_2022-09-24_13-52-54'].
  - Centroid [0.47200000000000003, 1.5149987936019897, 0.25507637496602176]
- 2 containing cell ['RP_207_2022-09-24_15-00-20'].
  - Centroid [0.68, 5.920087814331055, 0.3043298218537407]
- 3 containing cell ['RP_209_2022-09-24_15-05-43'].
  - Centroid [0.6880000000000001, 6.675105094909668, 0.42395945520096345]
- 4 containing cell ['RP_230_2022-09-24_16-06-55'].
  - Centroid [0.664, 7.770130157470703, 0.28580554464717195]

Isolated clusters will not be used for final matching.

## Matching

The clusters generate 5 matches using the specified parameters.
The matches, ordered by match metric, are as follows:

- metric used `power_opt_0`
- rank 0 match
  - cells ['RP_52_8_27_22', 'RP_56_8_27_22']
  - resulted in a metric of 7.997974037170412
- rank 1 match
  - cells ['RP_50_8_27_22', 'RP_57_8_27_22']
  - resulted in a metric of 7.389385155677797
- rank 2 match
  - cells ['RP_53_8_27_22', 'RP_59_8_27_22']
  - resulted in a metric of 7.090720036506655
- rank 3 match
  - cells ['RP_51_8_27_22', 'RP_58_8_27_22']
  - resulted in a metric of 6.601932895660402
- rank 4 match
  - cells ['RP_55_8_27_22', 'RP_5_8_27_22']
  - resulted in a metric of 5.057079683303834
