import.ny.borough.data <- function() {
	readOGR("shapefiles/nybb", "nybb") %>%
		spTransform(CRS("+proj=longlat +datum=WGS84")) %>%
		fortify %>%
		rename(lng = long) %>% 
		return
}

import.ny.facility.data <- function(){
	readOGR("shapefiles/Facilities_2015_shp", "Facilities") %>%
		spTransform(CRS("+proj=longlat +datum=WGS84")) %>%
		as.data.frame %>%
		rename(lng = coords.x1, lat = coords.x2) %>%
 		return
}

import.ny.waterfront.park.data <- function(){
	readOGR("shapefiles/nywaterfronts", "NYC_Waterfront_Parks") %>%
		spTransform(CRS("+proj=longlat +datum=WGS84")) %>%
		fortify %>%
		rename(lng = long) %>% 
 		return
}

import.ny.subway.stations <- function(all.stops = F){

	disambiguate.stations <- function(df){
		
		# helper function to duplicate stations that are coded for multiple 
		# routes

		rows.to.remove <- c()

		for (i in 1:nrow(df)){
			routes <- df$ROUTES[i] %>% strsplit(",") %>% unlist
			if (length(routes) > 1) {
				for (j in routes) {
					# make a copy of the current row
					# add it to the bottom of the data frame
					# then change the ROUTES entry so that it only has one
					# then finally we'll delete the duped entries below
					df <- rbind(df, df[i, ])
					df$ROUTES[nrow(df)] <- j

					# need to give the station a new unique id
					# this is a problem as it will generate a new 
					# hash each time, making it impossible 
					df$UNIQUEID[nrow(df)] <- digest(runif(1))
				}
				rows.to.remove <- c(rows.to.remove, i)
			}
		}

		df <- df[-rows.to.remove, ]
		return(df)
	}


	correct.ordering.of.stops <- function(df){
		
	  if(all.stops) return(df)
	  		
		route.orders$ROUTES <- as.character(route.orders$ROUTES)

		df %>%
			right_join(route.orders, by = c("OBJECTID", "ROUTES")) %>%
			group_by(BRANCH) %>%
			return

	}

	# main script
	readOGR("shapefiles/NYC_Subways", "subway_stations") %>%
		spTransform(CRS("+proj=longlat +datum=WGS84")) %>%
		as.data.frame %>%
		rename(lng = coords.x1, lat = coords.x2) %>%
		mutate(ROUTES = as.character(ROUTES)) %>%
		transform(UNIQUEID = OBJECTID) %>%
		transform(UNIQUEID = as.character(UNIQUEID)) %>%  #must be a bug in dplyr
		disambiguate.stations %>%
		correct.ordering.of.stops %>%
		return
}