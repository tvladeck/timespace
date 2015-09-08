new_theme_empty <- theme_bw()
new_theme_empty$line <- element_blank()
new_theme_empty$rect <- element_blank()
new_theme_empty$strip.text <- element_blank()
new_theme_empty$axis.text <- element_blank()
new_theme_empty$plot.title <- element_blank()
new_theme_empty$axis.title <- element_blank()
new_theme_empty$legend.position <- "none"

for (i in (99:20/100)) {
  span <- i
  boroughs.geom <- calc.boroughs.geom(nyb, span)
  geoms <- c(boroughs.geom) 
  current.plot <- overlay.geoms(geoms) + 
    coord_flip() + scale_x_reverse() + 
    scale_y_reverse() + new_theme_empty
  
  plot.name <- str_c("graphs/plot_", span, ".png")
  ggsave(filename = plot.name, plot = current.plot, width = 8.75, height = 8.75)
   
}