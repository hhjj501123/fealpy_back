import numpy as np
import matplotlib.pyplot as plt
import pytest

from fealpy.experimental.backend import backend_manager as bm
from fealpy.experimental.mesh.polygon_mesh import PolygonMesh
from fealpy.experimental.mesh.triangle_mesh import TriangleMesh
from fealpy.experimental.tests.mesh.polygon_mesh_data import *

class TestPolygonMeshInterfaces:
    @pytest.mark.parametrize("backend", ["numpy", "pytorch", "jax"])
    #@pytest.mark.parametrize("backend", ["numpy","pytorch"])
    @pytest.mark.parametrize("meshdata", init_data)
    def test_init(self,meshdata,backend):
        bm.set_backend(backend)
        node = bm.from_numpy(meshdata['node'])
        cell0 = bm.from_numpy(meshdata['cell'][0])
        if meshdata['cell'][1] is None:
            cell1 = None
        else:
            cell1 = bm.from_numpy(meshdata['cell'][1])
        cell = (cell0, cell1)
        mesh = PolygonMesh(node, cell)
        assert mesh.number_of_nodes() == meshdata["NN"]
        assert mesh.number_of_edges() == meshdata["NE"]
        assert mesh.number_of_faces() == meshdata["NF"]
        assert mesh.number_of_cells() == meshdata["NC"]
        face2cell = mesh.face2cell
        np.testing.assert_array_equal(face2cell, meshdata["face2cell"])
    
    @pytest.mark.parametrize("backend", ["numpy","pytorch","jax"])
    #@pytest.mark.parametrize("backend", ["jax"])
    @pytest.mark.parametrize("meshdata", entity_data)
    def test_entity(self,meshdata,backend):
        bm.set_backend(backend)
        node = bm.from_numpy(meshdata['node'])
        cell0 = bm.from_numpy(meshdata['cell'][0])
        q = meshdata['q']
        if meshdata['cell'][1] is None:
            cell1 = None
        else:
            cell1 = bm.from_numpy(meshdata['cell'][1])
        cell = (cell0, cell1)
        mesh = PolygonMesh(node, cell)

        assert mesh.entity_measure(0) == meshdata["entity_measure"][0]
        np.testing.assert_allclose(bm.to_numpy(mesh.entity_measure(1)),
                                   meshdata["entity_measure"][1],
                                   atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(mesh.entity_measure(2)),
                                   meshdata["entity_measure"][2],
                                   atol=1e-7)
        edge_barycenter = mesh.entity_barycenter('edge')
        cell_barycenter = mesh.entity_barycenter('cell')

        np.testing.assert_allclose(bm.to_numpy(edge_barycenter), meshdata["edge_barycenter"], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(cell_barycenter), meshdata["cell_barycenter"], atol=1e-7)
        boundary_node_index = mesh.boundary_node_index()
        boundary_cell_index = mesh.boundary_cell_index()
        boundary_face_index = mesh.boundary_face_index()
        
        np.testing.assert_array_equal(bm.to_numpy(boundary_node_index), meshdata["boundary_node_index"])
        np.testing.assert_array_equal(bm.to_numpy(boundary_face_index),meshdata["boundary_face_index"])
        np.testing.assert_array_equal(bm.to_numpy(boundary_cell_index), meshdata["boundary_cell_index"])
        integrator = mesh.quadrature_formula(q)
        bcs, ws = integrator.get_quadrature_points_and_weights()
        np.testing.assert_allclose(bm.to_numpy(bcs[0]), meshdata["bcs"][0], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(bcs[1]), meshdata["bcs"][1], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(bcs[2]), meshdata["bcs"][2], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(ws), meshdata["weight"], atol=1e-7)
        
        edge_integrator = mesh.quadrature_formula(q, 'edge',qtype='lobatto')
        edge_bcs, edge_ws = edge_integrator.get_quadrature_points_and_weights()

        np.testing.assert_allclose(bm.to_numpy(bcs[0]), meshdata["bcs"][0], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(bcs[1]), meshdata["bcs"][1], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(bcs[2]), meshdata["bcs"][2], atol=1e-7)
        np.testing.assert_allclose(bm.to_numpy(edge_ws), meshdata["edge_weight"], atol=1e-7)

    @pytest.mark.parametrize("backend", ["numpy","pytorch","jax"])
    #@pytest.mark.parametrize("backend", ["numpy"])
    @pytest.mark.parametrize("meshdata", extend_data)
    def test_extend_data(self,meshdata,backend):
        bm.set_backend(backend)
        node = bm.from_numpy(meshdata['node'])
        cell0 = bm.from_numpy(meshdata['cell'][0])
        p = meshdata['p']
        if meshdata['cell'][1] is None:
            cell1 = None
        else:
            cell1 = bm.from_numpy(meshdata['cell'][1])
        cell = (cell0, cell1)
        mesh = PolygonMesh(node, cell)

        ipoints = mesh.interpolation_points(p=p)
        np.testing.assert_allclose(bm.to_numpy(ipoints), meshdata["ipoints"],atol=1e-7)
        def f(p,index):
            x = p[...,0]
            y = p[...,1]
            val = x**2+y**2
            return val
        a1 = mesh.integral(f,q=3,celltype=False)
        a2 = mesh.integral(f,q=3,celltype=True)
        np.testing.assert_allclose(a1, meshdata["a1"], atol=1e-7)
        np.testing.assert_allclose(a2, meshdata["a2"], atol=1e-7)
    
    @pytest.mark.parametrize("backend", ["numpy","pytorch","jax"])
    @pytest.mark.parametrize("meshdata",geo_data)
    def test_geo_data(self,meshdata,backend):
        bm.set_backend(backend)
        node = bm.from_numpy(meshdata['node'])
        cell0 = bm.from_numpy(meshdata['cell'][0])
        if meshdata['cell'][1] is None:
            cell1 = None
        else:
            cell1 = bm.from_numpy(meshdata['cell'][1])
        cell = (cell0, cell1)
        mesh = PolygonMesh(node, cell)
       
        edge_normal = mesh.edge_normal()
        edge_unit_normal = mesh.edge_unit_normal()

    @pytest.mark.parametrize("backend", ["numpy","pytorch","jax"])
    @pytest.mark.parametrize("meshdata",mesh_example_data)
    def test_mesh_example(self,meshdata,backend):
        bm.set_backend(backend)
        mesh1 = PolygonMesh.from_one_triangle()
        edge1 = mesh1.entity('edge')
        edge2cell1 = mesh1.edge_to_cell()
        mesh2 = PolygonMesh.from_one_square()
        edge2 = mesh2.entity('edge')
        edge2cell2 = mesh2.edge_to_cell()
        mesh3 = PolygonMesh.from_one_pentagon()
        edge3 = mesh3.entity('edge')
        edge2cell3 = mesh3.edge_to_cell()
        mesh4 = PolygonMesh.from_one_hexagon()
        edge4 = mesh4.entity('edge')
        edge2cell4 = mesh4.edge_to_cell()
        np.testing.assert_array_equal(bm.to_numpy(edge1),meshdata["one_triangle_edge"]),
        np.testing.assert_array_equal(bm.to_numpy(edge2cell1),meshdata["one_triangle_edge2cell"])
        np.testing.assert_array_equal(bm.to_numpy(edge2),meshdata["one_square_edge"]),
        np.testing.assert_array_equal(bm.to_numpy(edge2cell2),meshdata["one_square_edge2cell"])
        np.testing.assert_array_equal(bm.to_numpy(edge3),meshdata["one_pentagon_edge"]),
        np.testing.assert_array_equal(bm.to_numpy(edge2cell3),meshdata["one_pentagon_edge2cell"])
        np.testing.assert_array_equal(bm.to_numpy(edge4),meshdata["one_hexagon_edge"]),
        np.testing.assert_array_equal(bm.to_numpy(edge2cell4),meshdata["one_hexagon_edge2cell"])
        node = bm.from_numpy(meshdata['triangle_node'])
        cell = bm.from_numpy(meshdata['triangle_cell'])
        mesh = TriangleMesh(node, cell)
        pmesh = PolygonMesh.from_mesh(mesh)
        pedge = pmesh.entity('edge')
        pedge2cell = pmesh.edge_to_cell()
        np.testing.assert_array_equal(bm.to_numpy(pedge),meshdata["pmesh_edge"]),
        np.testing.assert_array_equal(bm.to_numpy(pedge2cell),meshdata["pmesh_edge2cell"])

if __name__ == "__main__":
    pytest.main(["./test_polygon_mesh.py", "-k", "test_init"])
    pytest.main(["./test_polygon_mesh.py", "-k", "test_entity"])
    pytest.main(["./test_polygon_mesh.py", "-k", "test_extend_data"])
    pytest.main(["./test_polygon_mesh.py", "-k", "test_geo_data"])
    pytest.main(["./test_polygon_mesh.py", "-k", "test_mesh_example"])
    
    