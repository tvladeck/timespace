dist.mtx <- distance.matrix[1:current.row, -c(1,2,3)]
dist.mtx <- dist.mtx + t(dist.mtx)


transform.distance.matrix <- function(dist.mtx) { 
  # make sure the distance matrix is symmetric!!
  if(!(nrow(dist.mtx) == ncol(dist.mtx))) {print("this won't work")}
  
  cmd.scaled.dist.mtx <- as.data.frame(cmdscale(dist.mtx))
  cmd.scaled.dist.mtx$neighborhood <- distance.matrix$neighborhood[1:nrow(cmd.scaled.dist.mtx)]
  colnames(cmd.scaled.dist.mtx) <- c("dim1", "dim2", "neighborhood")
  rownames(cmd.scaled.dist.mtx) <- cmd.scaled.dist.mtx$neighborhood
  df <- cmd.scaled.dist.mtx
  return(df)
}

coord.mtx <- transform.distance.matrix(dist.mtx)
