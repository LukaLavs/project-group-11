from sage.all import *

G = Graph()

G.add_vertices([1, 2, 3, 4, 5])


G.add_edges([(1,2), (1,3), (2,3), (3,4), (4,5)])

print("Vertices:", G.vertices())
print("Edges:", G.edges())
print("Degree of each vertex:", G.degree())

plot = G.plot(vertex_labels=True, vertex_size=400, edge_color='blue', vertex_color='orange')

plot.save("images/sample_graph.png") # When running .sage file paths are relative to script