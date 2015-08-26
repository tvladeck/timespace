filter.to.convex.hull <- function(df){
  find.hull <- function(df){
    df[chull(df$dim1, df$dim2), ]
  }
  
  hulls <- ddply(df, "id", find.hull)
 
  return(hulls) 
}
