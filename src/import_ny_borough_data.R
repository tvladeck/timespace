import.ny.borough.data <- function() {
  nyboroughs <- readOGR("shapefiles/nybb", "nybb")
  nyboroughs <- spTransform(nyboroughs, CRS("+proj=longlat +datum=WGS84"))
  nyb <- fortify(nyboroughs)
  colnames(nyb)[1] <- "lng"
  return(nyb)
}