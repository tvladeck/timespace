# p.mtx <- cbind(coord.mtx, distance.matrix[1:nrow(coord.mtx), c(2,3)])
# t.mtx <- cbind(coord.mtx, distance.matrix[1:nrow(coord.mtx), c(3,4)])

p.d1 <- function(p.mtx, lat){
  
  lat.range             <- max(p.mtx$lat) - min(p.mtx$lat)
  lat.relative.position <- (lat - min(p.mtx$lat))/lat.range
  dim1.range            <- max(p.mtx$dim1) - min(p.mtx$dim1)
  return(min(p.mtx$dim1) + lat.relative.position * dim1.range)
  
}

p.d2 <- function(p.mtx, lng){
  
  lng.range             <- max(p.mtx$lng) - min(p.mtx$lng)
  lng.relative.position <- (lng - min(p.mtx$lng))/lng.range
  dim2.range            <- max(p.mtx$dim2) - min(p.mtx$dim2)
  return(min(p.mtx$dim2) + lng.relative.position * dim2.range)
  
}

create.transformation.matrix <- function(p.mtx){
  t.mtx <- data.frame(
    "lat"  = p.mtx$lat,
    "lng"  = p.mtx$lng,
    "dim1" = p.mtx$dim1, # where the projection ended up
    "dim2" = p.mtx$dim2, # same
    "sd1"  = p.d1(p.mtx, p.mtx$lat),
    "sd2"  = p.d2(p.mtx, p.mtx$lng),
    "cd1"  = p.mtx$dim1 - p.d1(p.mtx, p.mtx$lat), # change in dim1
    # - subtracting where it would have ended up w/ a naive starting point
    "cd2"  = p.mtx$dim2 - p.d2(p.mtx, p.mtx$lng)  # change in dim2
  )
  return(t.mtx)
}

project.individual.coordinates <- function(lat, lng, t.mtx){
  
  # project arbitrary (lat, lng) pair onto (dim1, dim2) using existing projection vectors
  # need table of existing transformation vectors - probably from coord.p.mtx and distance.matrix
  # expects input with columns lat, lng, dim1, dim2
  # convention is we're going to map lat->dim1 and lng->dim2

  distances <- ((lat - t.mtx$lat)^2 + (lng - t.mtx$lng)^2) %>% sqrt
  
  # need to check if any distances are zero and then return that exact xformation vector
  # to avoid divide by zero error
  if (0 %in% distances){
    
    idx <- match(0, distances)
    new.coords <- c("dim1" = p.mtx$dim1[idx], "dim2" = p.mtx$dim2[idx])
    return(new.coords)
    
  }
  
  weights   <- 1/(distances^2)
  
  starting.dim1 <- p.d1(t.mtx, lat) 
  starting.dim2 <- p.d2(t.mtx, lng)
  
  weighted.avg.dim1.xform <- sum(weights * t.mtx$cd1)/(sum(weights))
  weighted.avg.dim2.xform <- sum(weights * t.mtx$cd2)/(sum(weights))
  
  new.dim1 <- starting.dim1 + weighted.avg.dim1.xform
  new.dim2 <- starting.dim2 + weighted.avg.dim2.xform
  
  new.coords <- data.frame("dim1" = new.dim1, "dim2" = new.dim2)
  return(new.coords)
}

project.dim1 <- function(lat, lng, t.mtx){
  
  distances <- ((lat - t.mtx$lat)^2 + (lng - t.mtx$lng)^2) %>% sqrt
  if (0 %in% distances){
    
    idx <- match(0, distances)
    new.dim1 <- p.mtx$dim1[idx]
    return(new.coords)
    
  }
  
  weights   <- 1/(distances^2)
  
  starting.dim1 <- p.d1(t.mtx, lat) 
  weighted.avg.dim1.xform <- sum(weights * t.mtx$cd1)/(sum(weights))
  new.dim1 <- starting.dim1 + weighted.avg.dim1.xform
  return(new.dim1)
  
}

project.dim2 <- function(lat, lng, t.mtx){
  
  distances <- ((lat - t.mtx$lat)^2 + (lng - t.mtx$lng)^2) %>% sqrt
  if (0 %in% distances){
    
    idx <- match(0, distances)
    new.dim2 <- p.mtx$dim2[idx]
    return(new.dim2)
    
  }
  
  weights   <- 1/((distances^2))
  
  starting.dim2 <- p.d2(t.mtx, lng) 
  weighted.avg.dim2.xform <- sum(weights * t.mtx$cd2)/(sum(weights))
  new.dim2 <- starting.dim2 + weighted.avg.dim2.xform
  return(new.dim2)
  
}

v.project.dim1 <- Vectorize(project.dim1, vectorize.args = c("lat", "lng"))
v.project.dim2 <- Vectorize(project.dim2, vectorize.args = c("lat", "lng"))

project.list.of.coordinates <- function(latlnglist, t.mtx){
  
  latlnglist %>%
    mutate(dim1 = v.project.dim1(lat, lng, t.mtx)) %>%
    mutate(dim2 = v.project.dim2(lat, lng, t.mtx)) %>%
    return
  
}