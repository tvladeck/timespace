# fit new lat/lng coordinates to dim1 / dim2

fit.new.coordinates <- function(distance.matrix, lat.lng, poly.degree = 4){
  
  dist.mtx <- distance.matrix[1:(ncol(distance.matrix)-3), -c(1,2,3)]
  dist.mtx <- dist.mtx + t(dist.mtx)
  
  coord.mtx <- transform.distance.matrix(dist.mtx)
  original.coordinates <- distance.matrix[1:nrow(transformed.coordinates), 2:3]
  model.data <- cbind(transformed.coordinates, original.coordinates)
  
  model.dim1 <- lm(data = model.data, formula = dim1 ~ poly(lat, poly.degree) + poly(lng, poly.degree) + poly(lng * lat, poly.degree))
  model.dim2 <- lm(data = model.data, formula = dim2 ~ poly(lat, poly.degree) + poly(lng, poly.degree) + poly(lng * lat, poly.degree))
  
  fitted.dim1 <- predict.lm(model.dim1, lat.lng)
  fitted.dim2 <- predict.lm(model.dim2, lat.lng)
  
  df <- lat.lng
  df$dim1 <- fitted.dim1
  df$dim2 <- fitted.dim2
  
  return(df)
  
}


loess.fit.new.coordinates <- function(distance.matrix, lat.lng){
  
  dist.mtx <- distance.matrix[1:(ncol(distance.matrix)-3), -c(1,2,3)]
  dist.mtx <- dist.mtx + t(dist.mtx)
  
  coord.mtx <- transform.distance.matrix(dist.mtx)
  original.coordinates <- distance.matrix[1:nrow(coord.mtx), 2:3]
  transformed.coordinates <- coord.mtx[, 1:2]
  model.data <- cbind(transformed.coordinates, original.coordinates)
  
  model.dim1 <- loess(data = model.data, formula = dim1 ~ lat + lng, degree = 2, span = 0.3)
  model.dim2 <- loess(data = model.data, formula = dim2 ~ lat + lng, degree = 2, span = 0.3)
  
  fitted.dim1 <- predict(model.dim1, lat.lng, type = "response")
  fitted.dim2 <- predict(model.dim2, lat.lng, type = "response")
  
  df <- lat.lng
  df$dim1 <- fitted.dim1
  df$dim2 <- fitted.dim2
  
  return(df)
  
}
