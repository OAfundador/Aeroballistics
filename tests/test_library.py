"""The library interface (aeroballistics.Aerodynamics and aeroballistics.corrections)."""
import numpy as np
import pytest

import aeroballistics
from aeroballistics import corrections

P556 = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12, BD=1.00,
                         DIA=0.224, name="M855")


def test_no_correction_is_the_1973_program():
    a = aeroballistics.Aerodynamics(aeroballistics.M437)
    t = aeroballistics.table(aeroballistics.M437)
    for j, M in enumerate(aeroballistics.MACH_GRID):
        c = a(M)
        assert c.CX0 == pytest.approx(t["CX"][j]) and c["CMA"] == pytest.approx(t["CMA"][j])
    assert a.corrections == []


def test_linear_and_vectorized_interpolation():
    a = aeroballistics.Aerodynamics(aeroballistics.M437)
    M = np.array([0.7, 1.5, 2.25, 4.5])
    v = a.coefficient("CNA", M)
    assert v.shape == (4,)
    assert np.allclose(v, np.interp(M, aeroballistics.MACH_GRID, a.table["CNA"]))
    assert isinstance(a.coefficient("CNA", 2.25), float)


def test_modern_convention():
    s73 = aeroballistics.Aerodynamics(aeroballistics.M437)(2.0)
    mod = aeroballistics.Aerodynamics(aeroballistics.M437, convention="modern")(2.0)
    assert mod.Cmq_Cmad == pytest.approx(s73.CMQ / 2)          # qd/2V -> qd/V
    assert mod.Clp == pytest.approx(s73.CLP / 2)
    assert mod.Cmpa == pytest.approx(s73.CNPA / 2)
    assert mod.CDd2 == pytest.approx(s73.CX2 + s73.CNA)
    assert mod.CLa == pytest.approx(s73.CNA - s73.CX0)


def test_out_of_range():
    expected = aeroballistics.table(aeroballistics.M437)["CX"][-1]
    assert aeroballistics.Aerodynamics(aeroballistics.M437)(7.0).CX0 == pytest.approx(expected)
    assert np.isnan(aeroballistics.Aerodynamics(aeroballistics.M437, out_of_range="nan")(7.0).CX0)
    with pytest.raises(ValueError):
        aeroballistics.Aerodynamics(aeroballistics.M437, out_of_range="error")(7.0)


def test_correction_by_name_equal_to_the_experimental():
    a = aeroballistics.Aerodynamics(P556, "free_flight")
    assert [c.name for c in a.corrections] == ["free_flight"]
    assert np.all(a.table["CX"] > a.original_table["CX"])          # small bullet: more friction
    assert np.allclose(a.table["CPN"], P556.VCG - a.table["CMA"] / a.table["CNA"])


def test_choosing_a_single_coefficient():
    a = aeroballistics.Aerodynamics(P556, "free_flight:CX0")
    assert np.allclose(a.table["CNA"], a.original_table["CNA"])
    assert not np.allclose(a.table["CX"], a.original_table["CX"])


def test_scale_correction_requires_diameter():
    p = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51)
    with pytest.raises(ValueError):
        aeroballistics.Aerodynamics(p, "free_flight")
    assert aeroballistics.Aerodynamics(p, "free_flight", d_mm=5.69).context.d_mm == 5.69


def test_user_correction_and_registry():
    class CmaPlus10(corrections.Correction):
        name = "cma_plus_10"
        description = "CMα × 1.1 (example)"

        def apply(self, t, p, ctx):
            out = corrections.base.copy_table(t)
            out["CMA"] = out["CMA"] * 1.1
            return out

    a = aeroballistics.Aerodynamics(aeroballistics.M437, CmaPlus10())
    assert np.allclose(a.table["CMA"], 1.1 * a.original_table["CMA"])
    # derived columns recomputed: consistent CPN and s_g inversely proportional to CMα
    assert np.allclose(a.table["CPN"], aeroballistics.M437.VCG - a.table["CMA"] / a.table["CNA"])
    assert np.allclose(a.table["GYRO"], a.original_table["GYRO"] / 1.1)

    corrections.register("cma_plus_10", CmaPlus10)
    assert "cma_plus_10" in corrections.available()
    b = aeroballistics.Aerodynamics(aeroballistics.M437, ["cma_plus_10"])
    assert np.allclose(b.table["CMA"], a.table["CMA"])
    with pytest.raises(KeyError):
        aeroballistics.Aerodynamics(aeroballistics.M437, "does_not_exist")


def test_chaining_in_the_given_order():
    a = aeroballistics.Aerodynamics(P556, ["free_flight:CX0", "free_flight:CNA"])
    b = aeroballistics.Aerodynamics(P556, "free_flight")
    for col in ("CX", "CNA", "CPN"):
        assert np.allclose(a.table[col], b.table[col])


def test_alternative_data():
    k = aeroballistics.DataBlocks.from_listing()
    k.a[0] = k.a[0] + 0.01                      # XA1 + 0.01 -> CX + 0.01 at every Mach
    a = aeroballistics.Aerodynamics(aeroballistics.M437, data=k)
    assert np.allclose(a.table["CX"], a.original_table["CX"])        # original = with the same data
    assert np.allclose(a.table["CX"], aeroballistics.table(aeroballistics.M437)["CX"] + 0.01)


def test_magnus_moment_between_1_and_5_degrees():
    a = aeroballistics.Aerodynamics(aeroballistics.M437)
    c = a(2.0)
    assert a.magnus_moment(2.0, np.radians(1.0)) == pytest.approx(c.CNPA)
    assert a.magnus_moment(2.0, np.radians(5.0)) == pytest.approx(c.CNPA5)
    assert a.magnus_moment(2.0, np.radians(10.0)) == pytest.approx(c.CNPA5)


def test_core_api_at_the_top_level():
    """Everything aeroballistics.core exports is reachable from the package."""
    for name in ("table", "format_table", "geometry_warnings", "Projectile", "DataBlocks", "M437",
                 "MACH_GRID", "normal_and_moment", "stability", "read_card", "save_csv", "_main"):
        assert hasattr(aeroballistics, name), name
