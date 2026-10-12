import cadquery as cq

from cq_editor.cq_utils import _num, subshape_index, summarize_shape


def test_num_never_scientific():

    assert _num(0) == "0"
    assert _num(1e-12) == "0"  # dust snapped to zero
    assert _num(1.5) == "1.5"
    assert _num(2.0) == "2"  # trailing zeros stripped
    assert _num(68.0) == "68"
    assert _num(9.425) == "9.425"
    assert _num(40000) == "40000"  # would be 4e+04 under %.4g
    assert "e" not in _num(123456.789)
    assert "e" not in _num(0.0001234)


def test_subshape_index_roundtrip():

    shape = cq.Workplane("XY").box(10, 20, 4).val()

    for kind in (shape.Faces(), shape.Edges(), shape.Vertices()):
        for i, sub in enumerate(kind):
            assert subshape_index(shape, sub.wrapped) == i


def test_subshape_index_foreign_shape_is_none():

    shape = cq.Workplane("XY").box(10, 20, 4).val()
    other = cq.Workplane("XY").box(1, 1, 1).val()

    assert subshape_index(shape, other.Faces()[0].wrapped) is None


def test_summarize_solid():

    shape = cq.Workplane("XY").box(10, 20, 4).val()

    assert summarize_shape(shape) == "800 mm³, 640 mm², bbox 10 × 20 × 4 mm"


def test_summarize_plane_face():

    shape = cq.Workplane("XY").box(10, 20, 4).val()
    top = [f for f in shape.Faces() if f.normalAt().z > 0.99][0]

    summary = summarize_shape(top)
    assert summary.startswith("200 mm²")
    assert "normal (0, 0, 1)" in summary


def test_summarize_cylindrical_face_has_radius():

    shape = cq.Workplane("XY").box(10, 20, 4).edges("|Z").fillet(1.5).val()
    cyl = [f for f in shape.Faces() if f.geomType() == "CYLINDER"][0]

    assert "r 1.5 mm" in summarize_shape(cyl)


def test_summarize_edge():

    shape = cq.Workplane("XY").box(10, 20, 4).val()
    edge = shape.Edges()[0]

    summary = summarize_shape(edge)
    assert summary.endswith("mm")
    assert "e" not in summary  # no scientific notation


def test_summarize_circular_edge_has_radius_and_center():

    circle = cq.Workplane("XY").circle(3).val().Edges()[0]

    summary = summarize_shape(circle)
    assert "r 3 mm" in summary
    assert "center" in summary


def test_summarize_vertex_is_a_point():

    vertex = cq.Workplane("XY").box(10, 20, 4).val().Vertices()[0]

    summary = summarize_shape(vertex)
    assert summary.startswith("(") and summary.endswith(")")
    assert summary.count(",") == 2
