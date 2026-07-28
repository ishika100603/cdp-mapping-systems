# 02. Geoprocessing Submission

## My Dataset

`assignment-2-mapping.geojson` is a personal point dataset of the coffee shops, restaurants, bars, parks, and grocery/retail spots that make up my daily life outside of home and class, spanning Morningside Heights (near Columbia), the Upper West Side and Columbus Circle, Times Square and Hell's Kitchen, and the East Village.

Each point includes a `label` (place name plus address) and a `marker-symbol` indicating its category (restaurant, bar, cafe, bakery, park, grocery, city).

## Related Dataset

**MTA Subway Stations and Complexes** (New York State Open Data)
Link: https://data.ny.gov/Transportation/MTA-Subway-Stations-and-Complexes/5f5g-n3cz

This dataset lists all NYC subway and Staten Island Railway stations, aggregated by station complex, with station names, locations, Station IDs, Complex IDs, GTFS Stop IDs, the services that stop there, structure type, whether they fall within Manhattan's Central Business District, and ADA accessibility status.

## Why This Pairing

My dataset shows where I actually spend time day to day. Overlaying it with subway station locations lets me ask a simple but personal question: how much of my daily life is shaped by proximity to transit? Some of my "third places" (like the spots near Columbia) I go to because they're a short walk from where I live. Others (like Times Square or the East Village) I only visit because a direct subway line makes them easy to reach. Relating the two datasets turns a static list of places into a story about how transit access shapes where I choose to go.

## Proposed Methodology

1. Load both datasets into a notebook using `geopandas`, my GeoJSON points and the MTA Subway Stations and Complexes GeoJSON or CSV export.
2. Reproject both layers to the same coordinate reference system (for example a projected NY State Plane CRS) so distance calculations are in real world units (meters or feet) rather than degrees.
3. Nearest neighbor spatial join. For each of my personal points, use `geopandas.sjoin_nearest()` to find the closest subway station complex and compute the straight line distance to it.
4. Add derived columns to my points: `nearest_station`, `distance_to_station_m`.
5. Visualize.
   - Map: my points plotted on a basemap, sized or colored by distance to nearest subway station, with subway stations layered on top for reference.
   - Chart: a bar chart comparing average distance to transit across my four neighborhood clusters (Morningside Heights, UWS and Columbus Circle, Times Square, East Village), or across place categories (coffee, bar, restaurant, etc.).
6. Interpret. Discuss which places in my daily life are most and least transit accessible, and whether that access explains why I go there as often as I do.

