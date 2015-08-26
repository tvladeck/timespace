timeBetweenLocations <- function(row1, row2, data = addresses){
  address1 <- addresses[row1]
  address2 <- addresses[row2]
  if (routeQueryCheck() > 0){

  	tryCatch({
  			rt <- route(address1, address2, mode="transit")
  		}, error = function(e){
  			rt <- route(address2, address1, mode="transit")
  		}
  	)

  	time <- sum(rt$seconds)
  	return(time)
  }
  
}
