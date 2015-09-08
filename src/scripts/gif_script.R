
new_theme_empty <- theme_bw()
new_theme_empty$line <- element_blank()
new_theme_empty$rect <- element_blank()
new_theme_empty$strip.text <- element_blank()
new_theme_empty$axis.text <- element_blank()
new_theme_empty$plot.title <- element_blank()
new_theme_empty$axis.title <- element_blank()
new_theme_empty$legend.position <- "none"

for (i in 12:100 / 100) {

  span <- i
  subways.geom  <- calc.subways.geom(subways, span)
  nta.geom <- calc.nta.geom(nta, span)
  geoms <- c(nta.geom, subways.geom)

  current.plot <- overlay.geoms(geoms) + 
    coord_flip() + scale_x_reverse() + 
    scale_y_reverse() + new_theme_empty
  
  ggsave(filename = str_c("graphs/plot", (span*100),".png"),
         plot = current.plot,
         height = 8.75,
         width = 8.75)
}