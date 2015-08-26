#setwd("~/Dropbox (BPS)/Venmo_Analytics/Strategy Team/Tom V/map")
#setwd("~/Git/timespace")

prefixes <- c("functions/")

for (prefix in prefixes){
  src.files <- list.files(str_c("src/", prefix))
  for(src.file in src.files) {
    source(str_c("src/", prefix, src.file))  
  }
}

library('ProjectTemplate')
load("images/.RData")

load.project()
