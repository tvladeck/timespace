source("src/create_distance_matrix.R")
source("src/time_between_locations.R")

# confirm current row is correct
current.row <- ncol(distance.matrix) - 3

for(i in (current.row+1):(current.row+20)){
  distance.matrix <- addColumnToDistanceMatrix(i)
  print(paste("row", i, "done"))
  current.row <- i
}
  
save.image("images/.Rdata")
  	