import pandas as pd
from glob import glob
import os
import h3

p = os.path.join

def read_with_neighbors(TIME_DELTA=pd.Timedelta(7, 'days'), MAX_DATE='2019-04-29'):
    """
    Reads the data for each hexagon and averages with neighboring hexagons
    """
    X = read(TIME_DELTA, MAX_DATE)
    def mean_with_neighbors(tup):
        (h3id, timestamp) = tup
        ring = h3.k_ring(h3id, 1)
        idx = [(r, timestamp) for r in ring]
        neighborhood = X.reindex(idx)
        
        final = neighborhood.mean()
        final['bool_highway'] = neighborhood.bool_highway.max()
        final['bool_ramps'] = neighborhood.bool_ramps.max()
        return final.to_dict()
    return pd.DataFrame(list(X.index.map(mean_with_neighbors)), index=X.index)

def read(TIME_DELTA=pd.Timedelta(7, 'days'), MAX_DATE='2019-04-29'):
    X = pd.concat([pd.read_csv(f) for f in glob(p('..','02 Waze Data','chunks','*.csv'))])
    X['time'] = pd.to_datetime(X[['day', 'month', 'year']])
    X = X.drop(['day', 'month', 'year'], axis=1)
    X = X[X['time'] < MAX_DATE]
    X_res = X.groupby('h3id').resample(TIME_DELTA, on='time', origin=X.time.min())
    return prepare_features(X_res)

def prepare_features(X_res):
    X_mean = X_res.mean()
    X_min = X_res.min()
    X_max = X_res.max()
    X_sum = X_res.sum()
    avg_congested_prop = X_mean.max_length/X_max.counta
    avg_congested_prop.name = 'avg_congested_prop'
    
    X_final = pd.concat([
            avg_congested_prop,
            X_max[['max_length', 'bool_highway', 'bool_ramps']],
            X_sum[['count_highway', 'count_streets', 'count_primary', 'count_secondary', 'count_primary_street', 'count_primary_ramps']],
        ], axis=1)
    X_final['avg_speed'] = X_mean[['mean_speed']]
    X_final['min_median_level'] = X_min[['median_level']]
    
    return X_final[['avg_congested_prop', 'max_length', 'avg_speed', 'min_median_level',
           'bool_highway', 'bool_ramps', 'count_highway', 'count_streets',
           'count_primary', 'count_secondary', 'count_primary_street',
           'count_primary_ramps']]