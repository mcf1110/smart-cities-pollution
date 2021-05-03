import h3 as h3
import pandas as pd

def h3_to_poly(h3id):
     geo = h3.h3_to_geo_boundary(h3id)
     return ','.join([f'{g[0]} {g[1]}' for g in geo])
def many_h3_to_query(h3ids):
    polys = map(h3_to_poly, h3ids)


    whens = [f"WHEN ST_WITHIN(ST_POINT(line[1].y, line[1].x), ST_POLYGON('POLYGON(({poly}))')) THEN '{h3id}'" for (h3id, poly) in zip(h3ids, polys)]
    joined = " ".join(whens)
    
    return f"""
    WITH 
    desiredRegions AS (
        SELECT
              (CASE {joined} ELSE NULL END) as h3id,
              uuid, length, speed, level, day, roadtype
            FROM jams
            WHERE month = 4 AND year=2019 AND hour between 6 and 18
        ),
    daily AS (
            SELECT
              h3id,
              COUNT(uuid) as counta,
              MAX(length) as max_length,
              AVG(speed) as mean_speed,
              approx_percentile(level, 0.5) as median_level,
              MAX(CASE WHEN roadtype = 3 THEN 1 ELSE 0 END) as bool_highway,
              MAX(CASE WHEN roadtype = 4 THEN 1 ELSE 0 END) as bool_ramps,
              SUM(CASE WHEN roadtype = 3 THEN 1 ELSE 0 END) as count_highway,
              SUM(CASE WHEN roadtype = 1 THEN 1 ELSE 0 END) as count_streets,
              SUM(CASE WHEN roadtype = 6 THEN 1 ELSE 0 END) as count_primary,
              SUM(CASE WHEN roadtype = 7 THEN 1 ELSE 0 END) as count_secondary,
              SUM(CASE WHEN roadtype = 2 THEN 1 ELSE 0 END) as count_primary_street, 
              SUM(CASE WHEN roadtype = 4 THEN 1 ELSE 0 END) as count_primary_ramps
            FROM desiredRegions
            WHERE h3id IS NOT NULL
            GROUP BY day, h3id)
    SELECT 
        h3id,
        MAX(counta) as max_counta,
        AVG(max_length) / MAX(counta) as avg_congested_prop,
        MAX(max_length) as max_length,
        AVG(mean_speed) as avg_speed,
        MIN(median_level) as min_median_level,
        MAX(bool_highway) as bool_highway,
        MAX(count_highway) as bool_ramps,
        SUM(count_highway) as count_highway,
        SUM(count_streets) as count_streets,
        SUM(count_primary) as count_primary,
        SUM(count_secondary) as count_secondary,
        SUM(count_primary_street) as count_primary_street, 
        SUM(count_primary_ramps) as count_primary_ramps
    FROM daily
    GROUP BY h3id
    """
if __name__ == '__main__':
    df = pd.read_csv('../Quito/coordenadas.csv', sep=';')
    df['h3id'] = df.apply(lambda x: h3.geo_to_h3(x['Latitude'], x['Longitude'], 9), axis=1)
    print(many_h3_to_query(df.h3id))