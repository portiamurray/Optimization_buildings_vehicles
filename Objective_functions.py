def mincost(mdl):
    mdl.minimize(mdl.TotalCost)
    return mdl
def minco2(mdl):
    mdl.minimize(mdl.TotalCost*0.0001+mdl.TotalCO2)
    return mdl
def epmin(mdl,epconst):
    mdl.add_constraint(mdl.TotalCO2<=epconst)
    mdl.minimize(mdl.TotalCost)
    return mdl