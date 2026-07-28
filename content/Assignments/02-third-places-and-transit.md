# 02. Geoprocessing Submission

## My Dataset

`assignment-2-mapping.geojson` is a personal point dataset of the coffee shops, restaurants, bars, parks, and grocery and retail spots that make up my daily life outside of home and class, spanning Morningside Heights near Columbia, the Upper West Side and Columbus Circle, Times Square and Hell's Kitchen, and the East Village.

Each point includes a `label`, showing the place name plus address, and a `marker-symbol` indicating its category, such as restaurant, bar, cafe, bakery, park, grocery, or city.

## Related Dataset

**MTA Subway Stations and Complexes**, New York State Open Data
Link: https://data.ny.gov/Transportation/MTA-Subway-Stations-and-Complexes/5f5g-n3cz

This dataset lists all NYC subway and Staten Island Railway stations, aggregated by station complex, with station names, locations, Station IDs, Complex IDs, GTFS Stop IDs, the services that stop there, structure type, whether they fall within Manhattan's Central Business District, and ADA accessibility status.

## Why This Pairing

My dataset shows where I actually spend time day to day. Overlaying it with subway station locations lets me ask a simple but personal question: how much of my daily life is shaped by proximity to transit? Some of my third places near Columbia I go to because they're a short walk from where I live. Others, such as Times Square or the East Village, I only visit because a direct subway line makes them easy to reach. Relating the two datasets turns a static list of places into a story about how transit access shapes where I choose to go.

## Proposed Methodology

1. **Load both datasets** into a notebook using `geopandas`, my GeoJSON points and the MTA Subway Stations and Complexes GeoJSON or CSV export.
2. **Reproject** both layers to the same coordinate reference system, such as a projected NY State Plane CRS, so distance calculations come out in real world units like meters or feet rather than degrees.
3. **Nearest neighbor spatial join.** For each of my personal points, use `geopandas.sjoin_nearest()` to find the closest subway station complex and compute the straight line distance to it.
4. **Add derived columns** to my points: `nearest_station`, `distance_to_station_m`.
5. **Build connector lines.** For each point, construct a `LineString` geometry running from the point to its matched nearest station, so the relationship between the two datasets is visible directly on the map rather than only in a legend.
6. **Visualize.**
   - Map: my points and the subway stations plotted on a basemap, with a thin connector line drawn from each point to its nearest station.
   - Chart: a bar chart comparing average distance to transit across my four neighborhood clusters, Morningside Heights, UWS and Columbus Circle, Times Square, and East Village, or across place categories like coffee, bar, and restaurant.
7. **Interpret.** Discuss which places in my daily life are most and least transit accessible, and whether that access explains why I go there as often as I do.

## Workflow Diagram

See the accompanying workflow diagram for a visual outline of this process: load both datasets, reproject to a shared CRS, run the nearest neighbor join, add distance columns, build connector lines to the nearest station, then visualize and interpret.
