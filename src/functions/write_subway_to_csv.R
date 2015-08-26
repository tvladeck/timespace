write.subway.to.csv <- function(route){
  filter(all.subways, ROUTES == route) %>% 
    select(OBJECTID, ID, NAME, ROUTES) %>% 
    arrange(ID) %>% 
    write.csv(str_c("data/scratch_data/line_", route, ".csv"))
}


