# Assignment 5 — Web Mapping (Part 2)

## Overview

This assignment extends the API tutorial completed in class, which connects a MapLibre web map to a live Supabase backend containing the NYC Open Restaurants Inspections dataset. I added PostGIS spatial support to the dataset, wrote a SQL function to query the nearest restaurants to a clicked point, and extended the JavaScript to style the resulting points based on a chosen variable.

## The variable

I chose to visualize **`SeatingChoice`**, a categorical field indicating whether a restaurant's outdoor seating is on the **sidewalk**, the **roadway**, or **both**. This variable was appealing because it splits cleanly into three meaningful categories, and because it reflects a real policy distinction (roadway seating structures typically require different compliance standards than sidewalk seating).

## Styling approach

When the user clicks anywhere on the map, the app queries a custom PostgreSQL function (`find_nearest_n_restaurants`) that returns all restaurants within 1,000 meters of the clicked point, along with each restaurant's distance from that point. The results are rendered as a MapLibre circle layer styled with two data-driven `paint` properties:

* **Color** is mapped directly to `SeatingChoice`: red for sidewalk, blue for roadway, teal for both. This makes the categorical variable immediately readable at a glance.
* **Size and opacity** are both driven by `dist_meters` (distance from the clicked point). Closer restaurants render larger and more opaque; farther restaurants shrink and fade toward the edge of the 1,000-meter search radius. This gives the user an intuitive visual sense of proximity without needing to read exact numbers.

Clicking on an individual point opens a popup showing the restaurant's name, seating choice, and distance in meters, so the categorical color-coding is always backed by exact data on demand.

## Rationale

I chose to encode the categorical variable through **color** rather than size, since color is generally better suited to distinguishing category membership at a glance, while size and opacity are more naturally suited to representing a continuous variable like distance. Combining the two channels lets the map communicate two dimensions of information (what kind of seating, and how far away) without needing a more complex visual encoding or a separate control.

## Data / backend setup

* Dataset: NYC Open Restaurants Inspections (via NYC Open Data)
* Backend: Supabase (PostgreSQL + PostGIS), with a `geometry` column, spatial index, and public read-access policy configured on the `open-restaurant-inspections` table
* Query logic: custom `find_nearest_n_restaurants` PostgreSQL function using PostGIS distance functions, called via Supabase's RPC interface

## Submission

* Screenshots: `05-web-map-visualization-screenshot-1.png`, `05-web-map-visualization-screenshot-2.png`
* Web map files (live link): *to be added — GitHub Pages link*
