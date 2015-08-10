p.nyb <- project.list.of.coordinates(nyb, t.mtx)

p.nyb.cvx <- filter.to.convex.hull(p.nyb)

ggplot() + geom_polygon(data = filter(p.nyb, id == 3), aes(x=dim1, y=dim2, fill=id, group=group))

+
  geom_point(data = coord.mtx, aes(x=dim1, y=dim2))
       