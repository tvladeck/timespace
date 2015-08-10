timeBetweenLocations <- function(row1, row2, data = addresses){
  address1 <- addresses[row1]
  address2 <- addresses[row2]

  rt <- route(address1, address2, mode="transit")
  time <- sum(rt$seconds)
  return(time)
}
