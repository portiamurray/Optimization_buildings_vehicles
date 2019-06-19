def buildmodel(FuelPrice,FuelSellPrice,FuelCO2,kmdriven,VChargEff,DConvTech,BConvTech,ChargeAvailable,buildings,building2car,BEVtech,PHEVtech,Power_limit,TotalLimit,SpotPrice,pvmultiplier,year,Carriers,horizon,fullhorizon,NoStoreCarriers,cars,VTech,ConvTech,StorTech,DCycle,BLoads,annual_conversion,tdays,Areas,VDemandIn,AnnuityV,AnnuityC,AnnuityS,LifetimeV,LifetimeS,LifetimeC,CMatrix,Eff,Tank,CLim,VCost,VOMV,VTech_EE,CCost_slope,CCost_fixed,COMV,COMF,Conv_EE_slope,Conv_EE_fixed,CostS_slope,CostS_fixed,Stor_EE_fixed,Stor_EE_slope,SOMF,ChargEff,DischEff,Decay,MaxCharg,MaxDisch,MaxCapS,MaxCapC,MPL,MSU,mipgap):
    from docplex.mp.model import Model
    from docplex.util.environment import get_environment
    #h is for the typical days horizon
    #i is for the full horizon 0,8760
    #t is technologies on district level
    #pv is pv
    #f is for full carriers
    #s is for storage carriers
    #v for car technologies
    #cvh = [(c,v,h) for c in cars for v in VTech for h in horizon]
    tf = [(t,f) for t in DConvTech for f in Carriers]
    pvsb = [(pv,s,b) for pv in BConvTech for s in StorTech for b in buildings]
    pvbh = [(pv,b,h) for pv in BConvTech for b in buildings for h in horizon]
    th = [(t,h) for t in DConvTech for h in horizon]
    tfh = [(t,f,h) for t in DConvTech for h in horizon for f in Carriers]
    fh = [(f,h) for f in Carriers for h in horizon]
    fbh = [(f,b,h) for f in Carriers for b in buildings for h in horizon]
    sh = [(s,h) for s in StorTech for h in horizon]
    shfull = [(s,i) for s in StorTech for i in fullhorizon]
    vf= [(v,f) for v in VTech for f in Carriers]
    cv = [(c,v) for c in cars for v in VTech]
    cvf = [(c,v,f) for c in cars for v in VTech for f in Carriers]
    cvfh = [(c,v,f,h) for c in cars for v in VTech for f in Carriers for h in horizon]
    cvfdh = [(c,v,f,d,h) for d in DCycle for c in cars for v in VTech for f in Carriers for h in horizon]
    vfh=[(v,f,h) for v in VTech for f in Carriers for h in horizon]
    mdl = Model(name='P2GHub')
    #Design variables
    mdl.TechCap=mdl.continuous_var_dict(tf,lb=0,name='TechCap')
    mdl.yConv=mdl.binary_var_dict(tf,name='yConv')
    mdl.PVCap=mdl.continuous_var_dict(pvsb,name='PVCap')
    mdl.yPV=mdl.binary_var_dict(pvsb,name='yPV')
    mdl.StorCap=mdl.continuous_var_dict(StorTech,lb=0,name="StorCap")
    mdl.yStor=mdl.binary_var_dict(StorTech,name='yStor')
    mdl.Vehicles=mdl.binary_var_dict(cv,name='Vehicles')
    mdl.VStorage=mdl.continuous_var_dict(cvf,lb=0,name='VStorage')
    #Operation variables
    mdl.Pin=mdl.continuous_var_dict(th,lb=0,name="Pin")
    mdl.Pout=mdl.continuous_var_dict(tfh,lb=-100000,name="Pout")
    mdl.yOn=mdl.binary_var_dict(th,name="yOn")
    mdl.ySU=mdl.binary_var_dict(th,name='ySU')
    mdl.ySD=mdl.binary_var_dict(th,name='ySD')
    #mdl.dummyP=mdl.continuous_var_dict(tfh,lb=0,name='dummyP')
    mdl.PinPV=mdl.continuous_var_dict(pvbh, lb=0, name='PinPV')
    mdl.BImport=mdl.continuous_var_dict(fbh,lb=0,name='BImport')
    mdl.BExport=mdl.continuous_var_dict(fbh,lb=0,name='BExport')
    mdl.Import=mdl.continuous_var_dict(fh,lb=0,name='Import')
    mdl.Export=mdl.continuous_var_dict(fh,lb=0,name='Export')
    mdl.SpotElec=mdl.continuous_var_list(horizon,lb=0,name='SpotElec')
    mdl.Charging=mdl.continuous_var_dict(sh,lb=0,name='Charging')
    mdl.Discharging=mdl.continuous_var_dict(sh,lb=0,name='Discharging')
    mdl.PublicCharging=mdl.continuous_var_dict(cvfh,lb=0,name='PublicCharging')
    #mdl.PublicChargingSum=mdl.continuous_var_dict(vf,lb=0,name='PublicChargingSum')
    mdl.Level=mdl.continuous_var_dict(shfull,lb=0,name='Level')
    mdl.VCharging=mdl.continuous_var_dict(cvfh,lb=0,name='VCharging')
    #mdl.VChargingSum=mdl.continuous_var_dict(vf,lb=0,name='VChargingSum')
    mdl.VDischarging=mdl.continuous_var_dict(cvfdh,lb=0,name='VDischarging')
    mdl.VStorageLevel=mdl.continuous_var_dict(cvfh,lb=0,name='VStorageLevel')
    #Cost variables
    mdl.TechCapCost=mdl.continuous_var_dict(DConvTech,lb=0,name='TechCapCost')
    mdl.PVCapCost=mdl.continuous_var(lb=0,name='PVCapCost')
    mdl.FuelCost=mdl.continuous_var_dict(Carriers,lb=0,name='FuelCost')
    mdl.FuelSell=mdl.continuous_var_dict(Carriers,lb=0,name='FuelSell')
    mdl.StorCapCost=mdl.continuous_var_dict(StorTech,lb=0,name='StorCapCost')
    mdl.VCapCost=mdl.continuous_var_dict(VTech,lb=0,name='VCapCost')
    mdl.CarOM=mdl.continuous_var_dict(VTech,lb=0,name='CarOMV')
    mdl.StorOM=mdl.continuous_var(lb=0,name='StorOM')
    mdl.ConvOMF=mdl.continuous_var(lb=0,name='ConvOMF')
    mdl.ConvOMV=mdl.continuous_var(lb=0,name='ConvOMV')
    mdl.TechOM=mdl.continuous_var(lb=0,name='TechOM')
    mdl.SpotCosts=mdl.continuous_var(lb=0,name='SpotCosts')
    mdl.PublicCosts=mdl.continuous_var(lb=0,name='PublicCosts')
    mdl.TotalCost=mdl.continuous_var(lb=0,name='TotalCost')
    #CO2 variables
    mdl.TechEE=mdl.continuous_var_dict(DConvTech,lb=0,name='TechEE')
    mdl.PVEE=mdl.continuous_var(lb=0,name='PVEE')
    mdl.StorEE=mdl.continuous_var_dict(StorTech,lb=0,name='StorEE')
    mdl.VehicleEE=mdl.continuous_var_dict(VTech,lb=0,name='VehicleEE')
    mdl.FuelCO2=mdl.continuous_var_dict(Carriers,lb=0,name='FuelCO2')
    mdl.SpotCO2=mdl.continuous_var(lb=0,name='SpotCO2')
    mdl.PublicCO2=mdl.continuous_var(lb=0,name='PublicCO2')
    mdl.TotalCO2=mdl.continuous_var(lb=0,name='TotalCO2')
    #Add_constraints
    mdl.add_constraints(mdl.PinPV["PV",b,h]==BLoads[b,year].loc[h,'Solar']*mdl.PVCap["PV","Elec",b] for h in horizon for b in buildings)
    mdl.add_constraints(mdl.PVCap["PV","Elec",b]<=Areas.loc[b,'PV']*mdl.yPV["PV","Elec",b]*pvmultiplier for b in buildings)
    mdl.add_constraints(mdl.TechCap[t,f]<=MaxCapC[t]*mdl.yConv[t,f] for t in DConvTech for f in Carriers)
    mdl.add_constraints(mdl.sum(mdl.Vehicles[c,v] for v in VTech)==1 for c in cars)
    #Cmatrix conversion
    mdl.add_constraints(mdl.Pout[t,f,h]==mdl.Pin[t,h]*CMatrix[t,f,year] for t in DConvTech for f in Carriers for h in horizon)
    mdl.add_constraints(mdl.yOn[t,h]<=mdl.yConv[t,f] for t in DConvTech for f in Carriers for h in horizon)
    mdl.add_constraints(mdl.Pin[t,h]<=mdl.yOn[t,h]*MaxCapC[t] for t in DConvTech for h in horizon)
    mdl.add_constraints(mdl.Pout[t,f,h]<=mdl.TechCap[t,f] for h in horizon for f in Carriers for t in DConvTech)
    mdl.add_constraints(mdl.TechCap[t,f]*MPL[t]<=mdl.Pin[t,h]+MaxCapC[t]*(1-mdl.yOn[t,h]) for t in DConvTech for f in Carriers for h in horizon)
    #Start up shut down

    mdl.add_constraints(mdl.TechCap[t,f]*MSU[t]>=mdl.Pout[t,f,h]-MaxCapC[t]*(1-mdl.ySU[t,h]) for t in DConvTech for f in Carriers for h in horizon)
    mdl.add_constraints(mdl.TechCap[t,f]*MSU[t]>=mdl.Pout[t,f,h]-MaxCapC[t]*(1-mdl.ySD[t,h]) for t in DConvTech for f in Carriers for h in horizon)
    #Add storage
    mdl.add_constraints(mdl.VStorage[c,v,f]==Tank[(v,f,year)]*mdl.Vehicles[c,v] for c in cars for v in VTech for f in Carriers)
    mdl.add_constraints(mdl.VStorageLevel[c,v,f,h]<=mdl.VStorage[c,v,f] for c in cars for v in VTech for f in Carriers for h in horizon)
    mdl.add_constraints(mdl.StorCap[s]<=MaxCapS[s]*mdl.yStor[s] for s in StorTech)
    mdl.add_constraints(mdl.Level[s,i]<=mdl.StorCap[s] for s in StorTech for i in fullhorizon)

    mdl.add_constraints(mdl.VStorageLevel[c,v,"Elec",h]>=0.2*mdl.VStorage[c,v,"Elec"] for v in PHEVtech for c in cars for h in horizon)
    #Manage vehicle storage levels
    mdl.add_constraints(mdl.PublicCharging[c,v,"Petrol",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"H2",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"Heat",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"CH4",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"CO2",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"Water",h]==0 for h in horizon for c in cars for v in VTech)
    mdl.add_constraints(mdl.PublicCharging[c,v,"Elec",h]==0 for h in horizon for c in cars for v in VTech  if (v not in PHEVtech) and (v not in BEVtech))
    for h in horizon:
        if (h % 24)==0:
            mdl.add_constraints(mdl.VStorageLevel[c,v,f,h]==mdl.VStorageLevel[c,v,f,h+23]+VChargEff[f]*mdl.VCharging[c,v,f,h]+VChargEff[f]*mdl.PublicCharging[c,v,f,h]-mdl.sum(mdl.VDischarging[c,v,f,d,h] for d in DCycle) for c in cars for v in VTech for f in Carriers)
            mdl.add_constraints(mdl.ySU[t,h]-mdl.ySD[t,h]==mdl.yOn[t,h]-mdl.yOn[t,h+23] for t in DConvTech)
        else:
            mdl.add_constraints(mdl.ySU[t,h]-mdl.ySD[t,h]==mdl.yOn[t,h]-mdl.yOn[t,h-1] for t in DConvTech)
            mdl.add_constraints(mdl.VStorageLevel[c,v,f,h]==mdl.VStorageLevel[c,v,f,h-1]+VChargEff[f]*mdl.VCharging[c,v,f,h]+VChargEff[f]*mdl.PublicCharging[c,v,f,h]-mdl.sum(mdl.VDischarging[c,v,f,d,h] for d in DCycle) for c in cars for v in VTech for f in Carriers)
    #Manage long term stationary storages
    for i in fullhorizon:
        if i==0:
            mdl.add_constraints(mdl.Level[s,i]==mdl.Level[s,i+8759]*(1-Decay[s])+mdl.Charging[s,annual_conversion.loc[i,'Hours']]*ChargEff[s]-mdl.Discharging[s,annual_conversion.loc[i,'Hours']]*(1/DischEff[s])for s in StorTech)
        else:
            mdl.add_constraints(mdl.Level[s,i]==mdl.Level[s,i-1]*(1-Decay[s])+mdl.Charging[s,annual_conversion.loc[i,'Hours']]*ChargEff[s]-mdl.Discharging[s,annual_conversion.loc[i,'Hours']]*(1/DischEff[s])for s in StorTech)
    #Max charg and discharge rates
    mdl.add_constraints(mdl.Charging[s,h]<=mdl.StorCap[s]*MaxCharg[s] for h in horizon for s in StorTech)
    mdl.add_constraints(mdl.Discharging[s,h]<=mdl.StorCap[s]*MaxDisch[s] for h in horizon for s in StorTech)
    #Seasonal storage constraint
    mdl.add_constraints(mdl.Level[s,0]==mdl.Level[s,8759] for s in StorTech)
    #Building level energy balances
    mdl.add_constraints(mdl.BImport[f,b,h]+mdl.sum(CMatrix[t,f,year]*mdl.PinPV[t,b,h] for t in BConvTech)==BLoads[b,year].loc[h,f]+mdl.BExport[f,b,h]+mdl.sum(mdl.VCharging[c,v,f,h] for c in cars if c in building2car[b] for v in VTech) for b in buildings for h in horizon for f in Carriers)
    mdl.add_constraints(mdl.BImport["Elec",b,h]<=Power_limit.loc[b,'Limit_kW'] for b in buildings for h in horizon)
    mdl.add_constraints(mdl.BExport["Elec",b,h]<=Power_limit.loc[b,'Limit_kW'] for b in buildings for h in horizon)
    mdl.add_constraints(mdl.Export["Elec",h]<=TotalLimit for h in horizon)
    mdl.add_constraints(mdl.Import["Elec",h]<=TotalLimit for h in horizon)
    #Neighbourhood level energy balance
    mdl.add_constraints(mdl.Import[f,h]+mdl.SpotElec[h]+mdl.sum(mdl.Pout[t,f,h] for t in DConvTech)+mdl.sum(mdl.BExport[f,b,h] for b in buildings)-mdl.Charging[f,h]+mdl.Discharging[f,h]==mdl.sum(mdl.BImport[f,b,h] for b in buildings)/NetworkEff[f]+mdl.Export[f,h] for f in StorTech if f=="Elec" for h in horizon)
    mdl.add_constraints(mdl.Import[f,h]+mdl.sum(mdl.Pout[t,f,h] for t in DConvTech)+mdl.sum(mdl.BExport[f,b,h] for b in buildings)-mdl.Charging[f,h]+mdl.Discharging[f,h]==mdl.sum(mdl.BImport[f,b,h] for b in buildings)/NetworkEff[f]+mdl.Export[f,h] for f in StorTech if f!="Elec" for h in horizon)
    mdl.add_constraints(mdl.Import[f,h]+mdl.sum(mdl.Pout[t,f,h] for t in DConvTech)+mdl.sum(mdl.BExport[f,b,h] for b in buildings)>=mdl.sum(mdl.BImport[f,b,h] for b in buildings)+mdl.Export[f,h] for f in NoStoreCarriers for h in horizon)
    #Discharge of tank/battery times the efficiency loss must equal the demand
    mdl.add_constraints(mdl.sum(mdl.VDischarging[c,v,f,d,h]*Eff[d,v,f,year] for v in VTech for f in Carriers)==VDemandIn[d,year].loc[h,c] for h in horizon for c in cars for d in DCycle)
    mdl.add_constraints(mdl.VDischarging[c,v,"Petrol",d,h]>=mdl.VDischarging[c,v,"Elec",d,h]*0.5 for v in PHEVtech for c in cars for h in horizon for d in DCycle)##Check later!!!
    mdl.add_constraints(mdl.VCharging[c,v,f,h]<=ChargeAvailable.loc[h,c]*CLim[(v,f)]*mdl.Vehicles[c,v] for c in cars for v in VTech for f in Carriers for h in horizon)
    mdl.add_constraints(mdl.PublicCharging[c,v,f,h]<=22*(1-ChargeAvailable.loc[h,c])*mdl.Vehicles[c,v] for c in cars for v in VTech for f in Carriers for h in horizon)
    #Manage exports and imports
    mdl.add_constraints(mdl.SpotElec[h]<=mdl.Pin["PEME",h] for h in horizon)
    mdl.add_constraints(mdl.BImport["CO2",b,h]==0 for h in horizon for b in buildings)
    mdl.add_constraints(mdl.BExport["CO2",b,h]==0 for h in horizon for b in buildings)
    mdl.add_constraints(mdl.BExport["CH4",b,h]==0 for h in horizon for b in buildings)
    mdl.add_constraints(mdl.BExport["Heat",b,h]==0 for h in horizon for b in buildings)
    mdl.add_constraints(mdl.Import["Heat",h]==0 for h in horizon)
    mdl.add_constraints(mdl.Import["H2",h]==0 for h in horizon)
    mdl.add_constraints(mdl.Export["Heat",h]==0 for h in horizon)
    mdl.add_constraints(mdl.Export["H2",h]==0 for h in horizon)
    mdl.add_constraints(mdl.Export["Water",h]==0 for h in horizon)
    #Cannot export more than renewable production
    mdl.add_constraints(mdl.BExport["Elec",b,h]<=mdl.PinPV["PV",b,h]*CMatrix["PV","Elec",year] for h in horizon for b in buildings)
    mdl.add_constraints(mdl.Export["Elec",h]<=mdl.sum(mdl.BExport["Elec",b,h] for b in buildings)for h in horizon)
    mdl.add_constraints(mdl.Export["CH4",h]<=mdl.Pout["Methanation","CH4",h] for h in horizon)
    mdl.add_constraints(mdl.Export["Elec",h]<=mdl.sum(mdl.PinPV["PV",b,h]*CMatrix["PV","Elec",year] for b in buildings) for h in horizon)
    #Calculate costs
    mdl.add_constraints(mdl.TechCapCost[t]==mdl.sum(mdl.TechCap[t,f]*CCost_slope[t,f,year]+mdl.yConv[t,f]*CCost_fixed[t,f,year] for f in Carriers)*AnnuityC[t] for t in DConvTech)
    mdl.add_constraints(mdl.PVCapCost==mdl.sum(mdl.PVCap[t,"Elec",b]*CCost_slope[t,"Elec",year]+CCost_fixed[t,"Elec",year]*mdl.yPV[t,"Elec",b]for b in buildings)*AnnuityC[t] for t in BConvTech)
    mdl.add_constraints(mdl.StorCapCost[s]==(mdl.StorCap[s]*CostS_slope[s,year]+mdl.yStor[s]*CostS_fixed[s,year])*AnnuityS[s] for s in StorTech)
    mdl.add_constraints(mdl.VCapCost[v]==VCost[v,year]*mdl.sum(mdl.Vehicles[c,v]*AnnuityV.loc[year,c] for c in cars) for v in VTech)
    mdl.add_constraints(mdl.FuelCost[f]==mdl.sum(mdl.Import[f,h]*tdays.loc[h,'TDays'] for h in horizon)*FuelPrice[f,year] for f in Carriers)
    mdl.add_constraints(mdl.FuelSell[f]==mdl.sum(mdl.Export[f,h]*tdays.loc[h,'TDays'] for h in horizon)*FuelSellPrice[f,year] for f in Carriers)
    mdl.add_constraint(mdl.SpotCosts==mdl.sum(mdl.SpotElec[h]*tdays.loc[h,'TDays']*SpotPrice.loc[h,'Price'] for h in horizon))
    mdl.add_constraint(mdl.PublicCosts==mdl.sum(mdl.PublicCharging[c,v,f,h]*tdays.loc[h,'TDays'] for f in Carriers for c in cars for v in VTech for h in horizon)*0.40)
    mdl.add_constraints(mdl.CarOM[v]==mdl.sum(kmdriven.loc[year,c]*mdl.Vehicles[c,v]*VOMV[v] for c in cars) for v in VTech)
    mdl.add_constraint(mdl.StorOM==mdl.sum(mdl.StorCap[s]*SOMF[s] for s in StorTech))
    mdl.add_constraint(mdl.ConvOMF==mdl.sum(mdl.TechCap[t,f]*COMF[t,f] for f in Carriers for t in DConvTech))
    mdl.add_constraint(mdl.ConvOMV==mdl.sum(mdl.Pout[t,f,h]*COMV[t,f]*tdays.loc[h,'TDays'] for h in horizon for t in DConvTech for f in Carriers))
    mdl.add_constraint(mdl.TechOM==mdl.sum(mdl.CarOM[v] for v in VTech)+mdl.StorOM+mdl.ConvOMF+mdl.ConvOMV)
    mdl.add_constraint(mdl.TotalCost==mdl.PublicCosts+mdl.SpotCosts+mdl.PVCapCost+mdl.sum(mdl.VCapCost[v] for v in VTech)+mdl.sum(mdl.TechCapCost[t] for t in DConvTech)+mdl.sum(mdl.StorCapCost[s] for s in StorTech)+mdl.sum(mdl.FuelCost[f] for f in Carriers)+mdl.TechOM-mdl.sum(mdl.FuelSell[f] for f in Carriers))
    #Calculate CO2
    mdl.add_constraints(mdl.TechEE[t]==mdl.sum(mdl.TechCap[t,f]*Conv_EE_slope[t,f,year]+mdl.yConv[t,f]*Conv_EE_fixed[t,f,year] for f in Carriers)/LifetimeC[t] for t in DConvTech)
    mdl.add_constraint(mdl.PVEE==mdl.sum(mdl.PVCap["PV","Elec",b]*Conv_EE_slope["PV","Elec",year]+mdl.yPV["PV","Elec",b]*Conv_EE_fixed["PV","Elec",year] for b in buildings)/LifetimeC["PV"])
    mdl.add_constraints(mdl.StorEE[s]==(mdl.StorCap[s]*Stor_EE_slope[s,year]+mdl.yStor[s]*Stor_EE_fixed[s,year])/LifetimeS[s] for s in StorTech)
    mdl.add_constraint(mdl.SpotCO2==mdl.sum(mdl.SpotElec[h]*tdays.loc[h,'TDays'] for h in horizon)*FuelCO2["Elec",year])
    mdl.add_constraints(mdl.VehicleEE[v]==mdl.sum(mdl.Vehicles[c,v]/LifetimeV.loc[year,c] for c in cars)*VTech_EE[v,year] for v in VTech)
    mdl.add_constraints(mdl.FuelCO2[f]==mdl.sum(mdl.Import[f,h]*tdays.loc[h,'TDays']*FuelCO2[f,year] for h in horizon) for f in Carriers)
    mdl.add_constraint(mdl.PublicCO2==mdl.sum(mdl.PublicCharging[c,v,f,h]*tdays.loc[h,'TDays'] for f in Carriers for c in cars for v in VTech for h in horizon)*FuelCO2["Elec",year])
    mdl.add_constraint(mdl.TotalCO2==mdl.PublicCO2+mdl.SpotCO2+mdl.PVEE+mdl.sum(mdl.FuelCO2[f] for f in Carriers)+mdl.sum(mdl.VehicleEE[v] for v in VTech)+mdl.sum(mdl.TechEE[t] for t in DConvTech)+mdl.sum(mdl.StorEE[s] for s in StorTech))
    mdl.parameters.mip.tolerances.mipgap = mipgap
    return mdl