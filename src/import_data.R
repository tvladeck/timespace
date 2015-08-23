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

import.ny.subway.stations <- function(){

	disambiguate.stations <- function(df){
		
		# helper function to duplicate stations that are coded for multiple 
		# routes

		rows.to.remove <- c()

		for (i in 1:nrow(df)){
			stns <- df$ROUTES[i] %>% strsplit(",") %>% unlist
			if (length(stns) > 1) {
				for (j in stns){
					# make a copy of the current row
					# add it to the bottom of the data frame
					# then change the ROUTES entry so that it only has one
					# then finally we'll delete the duped entries below
					df <- rbind(df, df[i, ])
					df$ROUTES[nrow(df)] <- j
				}
				rows.to.remove <- c(rows.to.remove, i)
			}
		}

		df <- df[-rows.to.remove, ]
	}

	# main script
	readOGR("shapefiles/NYC_Subways", "subway_stations") %>%
		spTransform(CRS("+proj=longlat +datum=WGS84")) %>%
		as.data.frame %>%
		rename(lng = coords.x1, lat = coords.x2) %>%
		mutate(ROUTES = as.character(ROUTES)) %>%
		disambiguate.stations %>%
		return
}