nynta$lnglat <- lapply(nynta$NTAName, function(x) geocode(paste(x, ", nyc")))

nynta$lng <- unlist(lapply(nynta$lnglat, function(x) unlist(x[[1]])))
nynta$lat <- unlist(lapply(nynta$lnglat, function(x) unlist(x[[2]])))

nylnglat <- nynta[, c(1, 5, 9, 10)]

write.csv2(nylnglat, "data/nylnglat.csv")
