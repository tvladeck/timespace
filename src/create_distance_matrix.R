# the line below is run only once
# distance.matrix <- data.frame("neighborhood"=nylnglat$NTAName, "lat"=nylnglat$lat, "lng"=nylnglat$lng)


addColumnToDistanceMatrix <- function(number){
  # this function adds a row to the distance matrix
  # it takes a row number (i) and adds the ith column to the matrix
  
  
  distance.function <- function(x) { 
    Sys.sleep(1) 
    if(x>=number){0} else {timeBetweenLocations(x, number)}
  }
  


  distances <- unlist(lapply(1:nrow(distance.matrix), distance.function))
  
  
  name <- as.character(distance.matrix$neighborhood[number])
  ddf <- data.frame(name=distances)
  colnames(ddf) <- c(name)
  distance.matrix <- cbind(distance.matrix, ddf)
  filename <- paste("data/distance.matrix.", as.character(number), ".csv", sep = "")
  write.csv(distance.matrix, file = filename)
  
  current.row <- number
  
  return(distance.matrix)
}
