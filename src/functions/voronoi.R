
make.voronoi.plot <- function(coord.mtx){
  #coord.mtx needs to be a scaled distance matrix
  
  voronoi <- deldir(coord.mtx$dim1, coord.mtx$dim2)
  
  p <- ggplot(data = coord.mtx, aes(x=dim1, y=dim2)) + 
    geom_segment(
      aes(x = x1, y = y1, xend = x2, yend = y2), 
      size = 2,
      data = voronoi$dirsgs,
      linetype = 1,
      color = "#FFB958"
    ) +
#    geom_point(
#      fill = rgb(70,130,180,255,maxColorValue=255),
#      pch=21,
#      size = 4,
#      color="#333333"
#    )  + 
	geom_text(size = 3, data = coord.mtx, aes(x=dim1, y=dim2, label=rownames(coord.mtx)), position=position_jitter(width=4, height=4))
  
  return(p)
}


make.manhattan.voronoi.plot <- function(num.pts = 10000, coord.mtx){



  range.dim1 <- range(coord.mtx$dim1)[1]:range(coord.mtx$dim1)[2]
  range.dim2 <- range(coord.mtx$dim2)[1]:range(coord.mtx$dim2)[2]

  monte.carlo <- data.frame(dim1 = runif(num.pts, min(range.dim1), max(range.dim1)), dim2 = runif(num.pts, min(range.dim2), max(range.dim2)))


  distance.function  <- function(dim1, dim2, pair){

    abs(dim1 - pair$dim1) + abs(dim2 - pair$dim2)

  }

  closest.index <- function(distances){

    match(min(distances), distances)

  }

  monte.carlo$index <- 1:nrow(monte.carlo) %>% sapply(
      function(row){
        distance.function(monte.carlo$dim1[row], monte.carlo$dim2[row], coord.mtx) %>%
          closest.index %>%
          return
      }
    ) 

  

}
