boroughs.voronoi.overlay <- function(nyb, distance.matrix, bound = 5000){
  dist.mtx <- distance.matrix[1:(ncol(distance.matrix)-3), -c(1,2,3)]
  dist.mtx <- dist.mtx + t(dist.mtx)
  coord.mtx <- transform.distance.matrix(dist.mtx)
  
  p.mtx <- cbind(coord.mtx, distance.matrix[1:nrow(coord.mtx), c(2,3)])
  t.mtx <- create.transformation.matrix(p.mtx)


  voronoi <- deldir(coord.mtx$dim1, coord.mtx$dim2)
  
  
  
  #cvx.nyb <- project.list.of.coordinates(nyb, t.mtx)
  cvx.nyb <- loess.fit.new.coordinates(distance.matrix, nyb)
  
  #cvx.nyb <- filter.to.convex.hull(cvx.nyb)
  boroughs.geom <- cvx.nyb %>%
    geom_polygon(data = ., aes(x=dim1, y=dim2, fill=id, group=group))
  
  voronoi.segment.geom <- geom_segment(
    aes(x = x1, y = y1, xend = x2, yend = y2), 
    size = 2,
    data = voronoi$dirsgs,
    linetype = 1,
    color = "#FFB958"
  )
  
  voronoi.point.geom <- geom_point(
    data=coord.mtx, aes(x=dim1, y=dim2),
    fill = rgb(70,130,180,255,maxColorValue=255),
    pch=21,
    size = 4,
    color="#333333"
  ) 

  neighborhood.text.geom <- geom_text(size = 3, data = coord.mtx, aes(x=dim1, y=dim2, label=rownames(coord.mtx)), 
    position=position_jitter(width=4, height=4))
  
  bounds <- c(-bound, bound)
  
  ggplot() + boroughs.geom + 
    voronoi.segment.geom + 
    # neighborhood.text.geom +
    # voronoi.point.geom + 
    scale_x_continuous(limits = bounds) + 
    scale_y_continuous(limits = bounds)
  
}



