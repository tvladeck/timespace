# script to create graphs

boroughs.geom <- calc.boroughs.geom(nyb)
voronoi.geom  <- calc.voronoi.segment.geom(distance.matrix)
subways.geom  <- calc.subways.geom(subways)

geoms <- c(boroughs.geom, voronoi.geom, subways.geom)

plot <- overlay.geoms(geoms) + coord_flip() + scale_x_reverse() + scale_y_reverse()