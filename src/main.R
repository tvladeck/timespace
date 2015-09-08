
#setwd("~/Git/timespace")
#setwd("~/Dropbox (BPS)/Venmo_Analytics/Strategy Team/Tom V/map")

library('ProjectTemplate')
load("images/.RData")

load.project()

prefixes <- c("functions/")

for (prefix in prefixes){
  src.files <- list.files(str_c("src/", prefix))
  for(src.file in src.files) {
    source(str_c("src/", prefix, src.file))  
  }
}

