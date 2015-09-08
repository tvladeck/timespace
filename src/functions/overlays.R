span <- 0.3

calc.boroughs.geom <- function(nyb, span = 0.3){
  cvx.nyb <- loess.fit.new.coordinates(distance.matrix, nyb, span)
  
  boroughs.geom <- geom_polygon(
    data = cvx.nyb, 
    aes(x=dim1, y=dim2, fill=group, group=group)
  )
  
  return(boroughs.geom)
}

calc.nta.geom <- function(nta, span = 0.3){
  nta.coords <- loess.fit.new.coordinates(distance.matrix, nta)
  
  nta.geom <- geom_polygon(
    data = nta.coords,
    aes(x=dim1, y=dim2, fill=group, group=group)
  )
  
  return(nta.geom)
  
}

calc.subways.geom <- function(subways, span = 0.3){
  subway.coords <- loess.fit.new.coordinates(distance.matrix, subways, span)
  
  subways.geom <- geom_path(
    data = subway.coords, 
    aes(x=dim1, y=dim2, group=BRANCH)
  ) 

  return(subways.geom)

}

overlay.geoms <- function(geoms){

  plot <- ggplot()

  for (geom in geoms) plot <- plot + geom

  return(plot)

}

calc.voronoi.segment.geom <- function(distance.matrix){
  dist.mtx <- distance.matrix[1:(ncol(distance.matrix)-3), -c(1,2,3)]
  dist.mtx <- dist.mtx + t(dist.mtx)
  coord.mtx <- transform.distance.matrix(dist.mtx)
  
  p.mtx <- cbind(coord.mtx, distance.matrix[1:nrow(coord.mtx), c(2,3)])
  t.mtx <- create.transformation.matrix(p.mtx)


  voronoi <- deldir(coord.mtx$dim1, coord.mtx$dim2)

  voronoi.segment.geom <- geom_segment(
    aes(x = x1, y = y1, xend = x2, yend = y2), 
    size = 2,
    data = voronoi$dirsgs,
    linetype = 1,
    color = "#FFB958"
  )

  return(voronoi.segment.geom)
}
