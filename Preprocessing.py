def ProcessInputs(root):
    import pandas as pd
    import os

    def calculate_annuity(discount,index,Lifetime):
        Annuity={}
        for i in index:
            Annuity[i]=discount/(1-(1/((1+discount)**Lifetime[i])))
        return Annuity

    #root=r'D:/Portia/Mobility/Solothurn/' #Root directory of files
    path2018=root+'TDays2018.xls' #Demands and radiation for 2018 for 35 buildings (Electricity, Heating, Solar radiation)
    path2035=root+'TDays2035.xls'#Demands and radiation for 2035 for 35 buildings (Electricity, Heating, Solar radiation)
    path2050=root+'TDays2050.xls'#Demands and radiation for 2050 for 35 buildings (Electricity, Heating, Solar radiation)
    BLoads={}
    for i in range(0,35):
        sheetname='Group'+str(i+1)
        BLoads[i,2018]=pd.read_excel(path2018,sheetname,usecols='A:I')
        BLoads[i,2035]=pd.read_excel(path2035,sheetname,usecols='A:I')
        BLoads[i,2050]=pd.read_excel(path2050,sheetname,usecols='A:I')
    Areas=pd.read_excel(root+'Sonnendach_update.xlsx','Sheet1',usecols='B') #Import max roof area for PV for each building (from Sonnendach.ch)
    tday_conversion=[1,30,28,31,30,31,30,30,1,1,30,30,31,30,31]
    SpotPrice=pd.read_excel(root+'Electricity_price_2010_2016.xlsx','tdays') #Import spot market price
    Power_limit=pd.read_excel(root+'Power_limit.xlsx') #Max power limit of  each building
    TotalLimit=1152 #Total community power limit

    ##Establish typical days conversion to full horizon for seasonal storage
    annual_conversion=pd.DataFrame(index=range(0,8760),columns=['Hours'])
    tdays=pd.DataFrame(index=range(0,360),columns=['TDays'])
    a=0
    for i in range(0,len(tday_conversion)):
        beginhour=i*24
        for b in range(0,tday_conversion[i]):
            for h in range(0,24):
                annual_conversion.loc[a,'Hours']=beginhour+h
                a=a+1
    b=0
    for i in range(0,len(tday_conversion)):
        for h in range(0,24):
            tdays.loc[b,'TDays']=tday_conversion[i]
            b=b+1

    car2building=[13,13,13,25,20,20, 19, 20,20, 0, 0, 0,0,7, 7, 7, 7,4, 4, 4, 4, 34, 5, 5, 5,6, 6, 6, 1, 1, 1, 1,1,3, 3, 3, 3, 2, 2, 2, 2,2, 2, 33, 33, 31, 31, 30, 28,29, 29, 32, 23, 23, 24,26, 12,12, 13, 13, 8, 8, 9, 9, 10,10, 11, 14,14, 14, 17, 17,21, 21, 16, 18, 15]
    cars=['0-1','0-2','1-1','3-1','4-1','4-2','5-1','6-1','6-2','7-1','7-2','7-3','7-4','8-1','8-2','9-1','9-2','10-1',
           '10-2','10-3','10-4','11-1','12-1','12-2','12-3','13-1','14-1','15-1','16-1','16-2','16-3','16-4','16-5','17-1',
           '18-1','19-1','19-2','20-1','20-2','21-1','21-2','22-1','22-2','23-1','23-2','24-1','24-2','25-1','27-1','28-1',
           '28-2','29-1','30-1','30-2','31-1','32-1','33-1','34-1','35-1','35-2','36-1','37-1','38-1','38-2','39-1','39-2',
           '42-1','43-1','43-2','44-1','46-1','46-2','47-1','48-1','50-1','53-1','54-1']
    building2car={0:['7-1','7-2','7-3','7-4'],1:['16-1','16-2','16-3','16-4','16-5'],2:['20-1','20-2','21-1','21-2','22-1','22-2'],3:['17-1','18-1','19-1','19-2'],4:['10-1','10-2','10-3','10-4'],5:['12-1','12-2','12-3'],6:['13-1','14-1','15-1'],7:['8-1','8-2','9-1','9-2'],8:['36-1','37-1'],9:['38-1','38-2'],10:['39-1','39-2'],11:['42-1'],12:['33-1','34-1'],13:['35-1','35-2','0-1','0-2','1-1'],14:['43-1','43-2','44-1'],15:['54-1'],16:['50-1'],17:['46-1','46-2'],18:['53-1'],19:['5-1'],20:['4-1','4-2','6-1','6-2'],21:['47-1','48-1'],22:[],23:['30-1','30-2'],24:['31-1'],25:['3-1'],26:['32-1'],27:[],28:['27-1'],29:['28-1','28-2'],30:['25-1'],31:['24-1','24-2'],32:['29-1'],33:['23-1','23-2'],34:['11-1']}
    #Import vehicle driving demands. Please note that there are 3 driving cycles and demands are defined for each of these for each car in every hour
    VDemandIn={}
    VDemandIn['Highway',2018]=pd.read_excel(root+'Advanced_charging_profiles_monthly_380.xlsx','Highway',usecols='B:CE')
    VDemandIn['Average',2018]=pd.read_excel(root+'Advanced_charging_profiles_monthly_380.xlsx','Average',usecols='B:CE')
    VDemandIn['Urban',2018]=pd.read_excel(root+'Advanced_charging_profiles_monthly_380.xlsx','Urban',usecols='B:CE')
    VDemandIn['Highway',2035]=VDemandIn['Highway',2018]
    VDemandIn['Average',2035]=VDemandIn['Average',2018]
    VDemandIn['Urban',2035]=VDemandIn['Urban',2018]
    VDemandIn['Highway',2050]=VDemandIn['Highway',2018]
    VDemandIn['Average',2050]=VDemandIn['Average',2018]
    VDemandIn['Urban',2050]=VDemandIn['Urban',2018]
    #Charge available is a binary which states whether the car is at home (1) or not (0). Used to determine which type of charging is available in a time step
    ChargeAvailable=pd.read_excel(root+'Advanced_charging_profiles_monthly_380.xlsx','Charging',usecols='B:CE')
    #Discount rate and lifetimes are calculated for vehicles based on 200,000 km/year lifetime
    discount=0.06
    LifetimeV={}
    years=[2018,2035,2050]
    AnnuityV=pd.DataFrame(index=years,columns=cars)
    kmdriven=pd.DataFrame(index=years,columns=cars)
    LifetimeV=pd.DataFrame(index=years,columns=cars)
    for y in range(0,len(years)):
        for c in cars:
            vdurban=VDemandIn['Urban',years[y]][c]*tdays['TDays']
            vdaverage=VDemandIn['Average',years[y]][c]*tdays['TDays']
            vdhighway=VDemandIn['Highway',years[y]][c]*tdays['TDays']
            kmdriven.loc[years[y],c]=(vdurban.sum()+vdaverage.sum()+vdhighway.sum())
            LifetimeV.loc[years[y],c]=200000/kmdriven.loc[years[y],c]
            AnnuityV.loc[years[y],c]=discount/(1-(1/((1+discount)**LifetimeV.loc[years[y],c])))

    #Definitions of conversion technologies
    BConvTech=["PV"] #Technologies on the building level
    ConvTech=["Gas-boiler","PEMFC","PEME","Methanation","Heat-pump","PV"] #All Technologies
    DConvTech=["Gas-boiler","PEMFC","PEME","Methanation","Heat-pump"] #Technologies installed on district level
    LifetimeC={"Gas-boiler":25,"PEMFC":11,"PEME":11,"Methanation":20,"PV":25,"Heat-pump":20} #Lifetime of technologies
    MaxCapC={"Gas-boiler":1000,"PEMFC":1000,"PEME":1000,"Methanation":1000,"PV":1000,"Heat-pump":1000} #Maximum capacity of installation (please note that PV is redundant here as it is enforced by another constraint)
    Carriers=["Elec","Heat","H2","CH4","Petrol","CO2","Water"] #Set of energy carriers
    NoStoreCarriers=["Petrol","CO2","Water"] #Set of energy carriers that are not considered with storage
    #Fuel purchasing prices, selling prices, and CO2 emissions (inc. grey emissions values) for all carriers and years, which are considered with imports and exports of energy
    FuelPrice={("Elec",2018):0.2,("Heat",2018):50,('H2',2018):50,("CH4",2018):0.0934,("Petrol",2018):0.170,("CO2",2018):0.1,("Water",2018):0.001503,
               ("Elec",2035):0.24,("Heat",2035):50,('H2',2035):50,("CH4",2035):0.121,("Petrol",2035):0.2462,("CO2",2035): 0.08,("Water",2035):0.00175351,
              ("Elec",2050):0.26,("Heat",2050):50,('H2',2050):50,("CH4",2050):0.154,("Petrol",2050):0.37471,("CO2",2050): 0.06,("Water",2050):0.00200}
    FuelSellPrice={("Elec",2018):0.1,("Heat",2018):50,('H2',2018):0,("CH4",2018):0.0933,("Petrol",2018):0,("CO2",2018):0,("Water",2018):0,
                  ("Elec",2035):0.065,("Heat",2035):50,('H2',2035):0,("CH4",2035):0.012,("Petrol",2035):0,("CO2",2035):0,("Water",2035):0,
                  ("Elec",2050):0.035,("Heat",2050):50,('H2',2050):0,("CH4",2050):0.0153,("Petrol",2050):0,("CO2",2050):0,("Water",2050):0}
    FuelCO2={("Elec",2018):0.124,("Heat",2018):0,('H2',2018):0,("CH4",2018):0.235,("Petrol",2018):0.278,("CO2",2018):-0.8,("Water",2018):0.00027291,
            ("Elec",2035):0.1,("Heat",2035):0,('H2',2035):0,("CH4",2035):0.224,("Petrol",2035):0.278,("CO2",2035):-0.9,("Water",2035):0.00027291,
            ("Elec",2050):0.074,("Heat",2050):0,('H2',2050):0,("CH4",2050):0.2015,("Petrol",2050):0.278,("CO2",2050):-0.95,("Water",2050):0.00027291}
    #Energy carriers with Storage
    StorTech=["Elec","Heat","H2","CH4"] #Please note, elec refers to batteries, heat is a thermal energy storage tank, H2 is a compressed hydrogen storage, and CH4 is a CNG tank
    SOMF={"Elec":10,"Heat":0,"H2":0,"CH4":0} #Storage O&M Costs /kW installed or kg/h in the case of H2
    LifetimeS={"Elec":25,"Heat":17,"H2":20,"CH4":20} #Lifetime of storage technolgies
    ChargEff={"Elec":0.92,"Heat":0.9,"H2":0.99,"CH4":0.99} #Charging efficiency of storage system
    DischEff={"Elec":0.92,"Heat":1,"H2":0.99,"CH4":0.99} #Discharging efficiency of storage system
    Decay={"Elec":0.001,"Heat":0.01,"H2":0,"CH4":0} # loss of storage over time
    MaxCharg={"Elec":0.5,"Heat":0.25,"H2":0.5,"CH4":0.5} #Maximum % of charge of total volume
    MaxDisch={"Elec":0.5,"Heat":0.25,"H2":0.5,"CH4":0.5} #Max % discharge of total volume
    MaxCapS={"Elec":1000,"Heat":5000,"H2":5000,"CH4":5000} #Max install capacity
    AnnuityS=calculate_annuity(discount,StorTech,LifetimeS) #Annuity of storage
    #Linear Embodied emissions (EE) or grey emissions of technologies (kg CO2 eq /FU)
    Conv_EE_slope={("Gas-boiler","Heat",2018):51.2,
         ("Gas-boiler","CH4",2018):0,
         ("PEMFC","Elec",2018):26.63,
         ("PEMFC","Heat",2018):0,#heat/kg h2
         ("PEMFC","H2",2018):0,#h2 consumed
         ("PEME","H2",2018):1559,#kg h2/kWh elec
         ("PEME","Elec",2018):0,#kwh elec consumed
         ("Methanation","CH4",2018):6.66, #kwh CH4/kg H2
         ("Methanation","H2",2018):0,#kg h2
         ("Methanation","CO2",2018):0,#kg hydrogen
         ("Methanation","Elec",2018):0,
         ("Methanation","Heat",2018):0,#heat methanizer
         ("PV","Elec",2018):49.8,
         ("Heat-pump","Elec",2018):0,#
         ("Heat-pump","Heat",2018):74.76,#
         ("Gas-boiler","Elec",2018):0,("Gas-boiler","H2",2018):0,("Gas-boiler","Petrol",2018):0,("Gas-boiler","CO2",2018):0,("Gas-boiler", "Water",2018):0,("PEMFC","CH4",2018):0,("PEMFC","Petrol",2018):0,
         ("PEMFC","CO2",2018):0,("PEMFC","Water",2018):0,("PEME","Heat",2018):0,("PEME","CH4",2018):0,("PEME","Petrol",2018):0,("PEME","CO2",2018):0,("PEME","Water",2018):0,("Methanation","Petrol",2018):0,("Methanation","Water",2018):0,("PV","Heat",2018):0,("PV","H2",2018):0,
         ("PV","CH4",2018):0,("PV","Petrol",2018):0,("PV","CO2",2018):0,("PV","Water",2018):0,("Heat-pump","H2",2018):0,("Heat-pump","CH4",2018):0,("Heat-pump","Petrol",2018):0,("Heat-pump","CO2",2018):0,("Heat-pump","Water",2018):0,
         ("Gas-boiler","Heat",2035):51.2,
         ("Gas-boiler","CH4",2035):0,
         ("PEMFC","Elec",2035):24.21,
         ("PEMFC","Heat",2035):0,#heat/kg h2
         ("PEMFC","H2",2035):0,#h2 consumed
         ("PEME","H2",2035):1559,#kg h2/kWh elec
         ("PEME","Elec",2035):0,#kwh elec consumed
         ("Methanation","CH4",2035):6.66, #kwh CH4/kg H2
         ("Methanation","H2",2035):0,#kg h2
         ("Methanation","CO2",2035):0,#kg hydrogen
         ("Methanation","Elec",2035):0,
         ("Methanation","Heat",2035):0,#heat methanizer
         ("PV","Elec",2035):39.8,
         ("Heat-pump","Elec",2035):0,#
         ("Heat-pump","Heat",2035):64.08,#
         ("Gas-boiler","Elec",2035):0,("Gas-boiler","H2",2035):0,("Gas-boiler","Petrol",2035):0,("Gas-boiler","CO2",2035):0,("Gas-boiler","Water",2035):0,("PEMFC","CH4",2035):0,("PEMFC","Petrol",2035):0,
         ("PEMFC","CO2",2035):0,("PEMFC","Water",2035):0,("PEME","Heat",2035):0,("PEME","CH4",2035):0,("PEME","Petrol",2035):0,("PEME","CO2",2035):0,("PEME","Water",2035):0,("Methanation","Petrol",2035):0,("Methanation","Water",2035):0,("PV","Heat",2035):0,("PV","H2",2035):0,
         ("PV","CH4",2035):0,("PV","Petrol",2035):0,("PV","CO2",2035):0,("PV","Water",2035):0,("Heat-pump","H2",2035):0,("Heat-pump","CH4",2035):0,("Heat-pump","Petrol",2035):0,("Heat-pump","CO2",2035):0,("Heat-pump","Water",2035):0,
         ("Gas-boiler","Heat",2050):51.2,
         ("Gas-boiler","CH4",2050):0,
         ("PEMFC","Elec",2050):22.192,
         ("PEMFC","Heat",2050):0,#heat/kg h2
         ("PEMFC","H2",2050):0,#h2 consumed
         ("PEME","H2",2050):1559,#kg h2/kWh elec
         ("PEME","Elec",2050):0,#kwh elec consumed
         ("Methanation","CH4",2050):6.666, #kwh CH4/kg H2
         ("Methanation","H2",2050):0,#kg h2
         ("Methanation","CO2",2050):0,#kg hydrogen
         ("Methanation","Elec",2050):0,
         ("Methanation","Heat",2050):0,#heat methanizer
         ("PV","Elec",2050):29.8,
         ("Heat-pump","Elec",2050):0,#
         ("Heat-pump","Heat",2050):56.07,#
         ("Gas-boiler","Elec",2050):0,("Gas-boiler","H2",2050):0,("Gas-boiler","Petrol",2050):0,("Gas-boiler","CO2",2050):0,("Gas-boiler","Water",2050):0,("PEMFC","CH4",2050):0,("PEMFC","Petrol",2050):0,
         ("PEMFC","CO2",2050):0,("PEMFC","Water",2050):0,("PEME","Heat",2050):0,("PEME","CH4",2050):0,("PEME","Petrol",2050):0,("PEME","CO2",2050):0,("PEME","Water",2050):0,("Methanation","Petrol",2050):0,("Methanation","Water",2050):0,("PV","Heat",2050):0,("PV","H2",2050):0,
         ("PV","CH4",2035):0,("PV","Petrol",2050):0,("PV","CO2",2050):0,("PV","Water",2050):0,("Heat-pump","H2",2050):0,("Heat-pump","CH4",2050):0,("Heat-pump","Petrol",2050):0,("Heat-pump","CO2",2050):0,("Heat-pump","Water",2050):0}#you can add heat for electrolyser
    #Linear Embodied emissions (EE) or grey emissions of technologies (kg CO2 eq /FU)
    Conv_EE_fixed={("Gas-boiler","Heat",2018):0,
         ("Gas-boiler","CH4",2018):0,
         ("PEMFC","Elec",2018):528,
         ("PEMFC","Heat",2018):0,#heat/kg h2
         ("PEMFC","H2",2018):0,#h2 consumed
         ("PEME","H2",2018):30910,#kg h2/kWh elec
         ("PEME","Elec",2018):0,#kwh elec consumed
         ("Methanation","CH4",2018):10, #kwh CH4/kg H2
         ("Methanation","H2",2018):0,#kg h2
         ("Methanation","CO2",2018):0,#kg hydrogen
         ("Methanation","Elec",2018):0,
         ("Methanation","Heat",2018):0,#heat methaizer
         ("PV","Elec",2018):245,
         ("Heat-pump","Elec",2018):0,#
         ("Heat-pump","Heat",2018):2329,#
         ("Gas-boiler","Elec",2018):0,("Gas-boiler","H2",2018):0,("Gas-boiler","Petrol",2018):0,("Gas-boiler","CO2",2018):0,("Gas-boiler", "Water",2018):0,("PEMFC","CH4",2018):0,("PEMFC","Petrol",2018):0,
         ("PEMFC","CO2",2018):0,("PEMFC","Water",2018):0,("PEME","Heat",2018):0,("PEME","CH4",2018):0,("PEME","Petrol",2018):0,("PEME","CO2",2018):0,("PEME","Water",2018):0,("Methanation","Petrol",2018):0,("Methanation","Water",2018):0,("PV","Heat",2018):0,("PV","H2",2018):0,
         ("PV","CH4",2018):0,("PV","Petrol",2018):0,("PV","CO2",2018):0,("PV","Water",2018):0,("Heat-pump","H2",2018):0,("Heat-pump","CH4",2018):0,("Heat-pump","Petrol",2018):0,("Heat-pump","CO2",2018):0,("Heat-pump","Water",2018):0,
         ("Gas-boiler","Heat",2035):0,
         ("Gas-boiler","CH4",2035):0,
         ("PEMFC","Elec",2035):480,
         ("PEMFC","Heat",2035):0,#heat/kg h2
         ("PEMFC","H2",2035):0,#h2 consumed
         ("PEME","H2",2035):28532,#kg h2/kWh elec
         ("PEME","Elec",2035):0,#kwh elec consumed
         ("Methanation","CH4",2035):10, #kwh CH4/kg H2
         ("Methanation","H2",2035):0,#kg h2
         ("Methanation","CO2",2035):0,#kg hydrogen
         ("Methanation","Elec",2035):0,
         ("Methanation","Heat",2035):0,#heat methanizer
         ("PV","Elec",2035):196,
         ("Heat-pump","Elec",2035):0,#
         ("Heat-pump","Heat",2035):1996.29,#
         ("Gas-boiler","Elec",2035):0,("Gas-boiler","H2",2035):0,("Gas-boiler","Petrol",2035):0,("Gas-boiler","CO2",2035):0,("Gas-boiler","Water",2035):0,("PEMFC","CH4",2035):0,("PEMFC","Petrol",2035):0,
         ("PEMFC","CO2",2035):0,("PEMFC","Water",2035):0,("PEME","Heat",2035):0,("PEME","CH4",2035):0,("PEME","Petrol",2035):0,("PEME","CO2",2035):0,("PEME","Water",2035):0,("Methanation","Petrol",2035):0,("Methanation","Water",2035):0,("PV","Heat",2035):0,("PV","H2",2035):0,
         ("PV","CH4",2035):0,("PV","Petrol",2035):0,("PV","CO2",2035):0,("PV","Water",2035):0,("Heat-pump","H2",2035):0,("Heat-pump","CH4",2035):0,("Heat-pump","Petrol",2035):0,("Heat-pump","CO2",2035):0,("Heat-pump","Water",2035):0,
         ("Gas-boiler","Heat",2050):0,
         ("Gas-boiler","CH4",2050):0,
         ("PEMFC","Elec",2050):440,
         ("PEMFC","Heat",2050):0,#heat/kg h2
         ("PEMFC","H2",2050):26494,#h2 consumed
         ("PEME","H2",2050):0,#kg h2/kWh elec
         ("PEME","Elec",2050):0,#kwh elec consumed
         ("Methanation","CH4",2050):10, #kwh CH4/kg H2
         ("Methanation","H2",2050):0,#kg h2
         ("Methanation","CO2",2050):0,#kg hydrogen
         ("Methanation","Elec",2050):0,
         ("Methanation","Heat",2050):0,#heat methanizer
         ("PV","Elec",2050):150,
         ("Heat-pump","Elec",2050):0,#
         ("Heat-pump","Heat",2050):1746.75,#
         ("Gas-boiler","Elec",2050):0,("Gas-boiler","H2",2050):0,("Gas-boiler","Petrol",2050):0,("Gas-boiler","CO2",2050):0,("Gas-boiler","Water",2050):0,("PEMFC","CH4",2050):0,("PEMFC","Petrol",2050):0,
         ("PEMFC","CO2",2050):0,("PEMFC","Water",2050):0,("PEME","Heat",2050):0,("PEME","CH4",2050):0,("PEME","Petrol",2050):0,("PEME","CO2",2050):0,("PEME","Water",2050):0,("Methanation","Petrol",2050):0,("Methanation","Water",2050):0,("PV","Heat",2050):0,("PV","H2",2050):0,
         ("PV","CH4",2035):0,("PV","Petrol",2050):0,("PV","CO2",2050):0,("PV","Water",2050):0,("Heat-pump","H2",2050):0,("Heat-pump","CH4",2050):0,("Heat-pump","Petrol",2050):0,("Heat-pump","CO2",2050):0,("Heat-pump","Water",2050):0}

    Stor_EE_slope={("Elec",2018):40.49,("Heat",2018):4.68,("H2",2018):6.337,("CH4",2018):0.6416,
                   ("Elec",2035):24.528,("Heat",2035):4.68,("H2",2035):5.82,("CH4",2035):0.605,
                   ("Elec",2050):15.768,("Heat",2050):4.68,("H2",2050):4.85,("CH4",2050):0.55}
    Stor_EE_fixed={("Elec",2018):155.73,("Heat",2018):31,("H2",2018):744,("CH4",2018):64.167,
                   ("Elec",2035):116.8,("Heat",2035):31,("H2",2035):679,("CH4",2035):55,
                   ("Elec",2050):87.6,("Heat",2050):31,("H2",2050):582,("CH4",2050):55}

    CostS_slope={("Elec",2018):343.333,("Heat",2018):12.6,("H2",2018):295.26,("CH4",2018):4.83,
                 ("Elec",2035):142.5,("Heat",2035):12.6,("H2",2035):265.57,("CH4",2035):4.375,
                 ("Elec",2050):120,("Heat",2050):12.6,("H2",2050):243,("CH4",2050):4}
    CostS_fixed={("Elec",2018):6167,("Heat",2018):1685,("H2",2018):46620,("CH4",2018):766.67,
                 ("Elec",2035):2250,("Heat",2035):1685,("H2",2035):38295,("CH4",2035):675,
                 ("Elec",2050):1500,("Heat",2050):1685,("H2",2050):33300,("CH4",2050):600}
    #Efficiency of each technology in each year
    CMatrix={("Gas-boiler","Heat",2018):0.88,#kwh heat/kWh ng
         ("Gas-boiler","CH4",2018):-1,#kwh ng consumed
         ("PEMFC","Elec",2018):16.65,#c/kg h2
         ("PEMFC","Heat",2018):13.32,#heat/kg h2
         ("PEMFC","H2",2018):-1,#h2 consumed
         ("PEME","H2",2018):0.01802,#kg h2/kWh elec
         ("PEME","Elec",2018):-1.05,#kwh elec consumed
         ("PEME","Water",2018):-0.1802,#kg water
         ("Methanation","CH4",2018):26.307, #kwh CH4/kg H2
         ("Methanation","H2",2018):-1,#kg h2
         ("Methanation","CO2",2018):-5.2,#kg hydrogen
         ("Methanation","Elec",2018):-2.6307,
         ("Methanation","Heat",2018):0.333,#heat methanation
         ("PV","Elec",2018):0.17,#% efficient kW/kW
         ("Heat-pump","Elec",2018):-1,#
         ("Heat-pump","Heat",2018):3,#COP
         ("Gas-boiler","Elec",2018):0,("Gas-boiler","H2",2018):0,("Gas-boiler","Petrol",2018):0,("Gas-boiler","CO2",2018):0,("Gas-boiler","Water",2018):0,("PEMFC","CH4",2018):0,("PEMFC","Petrol",2018):0,
         ("PEMFC","CO2",2018):0,("PEMFC","Water",2018):0,("PEME","Heat",2018):0,("PEME","CH4",2018):0,("PEME","Petrol",2018):0,("PEME","CO2",2018):0,("Methanation","Petrol",2018):0,("Methanation","Water",2018):0,("PV","Heat",2018):0,("PV","H2",2018):0,
         ("PV","CH4",2018):0,("PV","Petrol",2018):0,("PV","CO2",2018):0,("PV","Water",2018):0,("Heat-pump","H2",2018):0,("Heat-pump","CH4",2018):0,("Heat-pump","Petrol",2018):0,("Heat-pump","CO2",2018):0,("Heat-pump","Water",2018):0,
         ("Gas-boiler","Heat",2035):0.9,#kwh heat/kWh ng
         ("Gas-boiler","CH4",2035):-1,#kwh ng consumed
         ("PEMFC","Elec",2035):18.32,#c/kg h2
         ("PEMFC","Heat",2035):11.65,#heat/kg h2
         ("PEMFC","H2",2035):-1,#h2 consumed
         ("PEME","H2",2035):0.01952,#kg h2/kWh elec
         ("PEME","Elec",2035):-1.05,#kwh elec consumed
         ("PEME","Water",2035):-0.1952,#kg water
         ("Methanation","CH4",2035):26.307, #kwh CH4/kg H2
         ("Methanation","H2",2035):-1,#kg h2
         ("Methanation","CO2",2035):-5.2,#kg hydrogen
         ("Methanation","Elec",2035):-2.6307,#kWh/kg H2
         ("Methanation","Heat",2035):0.666,#heat methanation
         ("PV","Elec",2035):0.19,
         ("Heat-pump","Elec",2035):-1,#
         ("Heat-pump","Heat",2035):3.5,#
         ("Gas-boiler","Elec",2035):0,("Gas-boiler","H2",2035):0,("Gas-boiler","Petrol",2035):0,("Gas-boiler","CO2",2035):0,("Gas-boiler","Water",2035):0,("PEMFC","CH4",2035):0,("PEMFC","Petrol",2035):0,
         ("PEMFC","CO2",2035):0,("PEMFC","Water",2035):0,("PEME","Heat",2035):0,("PEME","CH4",2035):0,("PEME","Petrol",2035):0,("PEME","CO2",2035):0,("Methanation","Petrol",2035):0,("Methanation","Water",2035):0,("PV","Heat",2035):0,("PV","H2",2035):0,
         ("PV","CH4",2035):0,("PV","Petrol",2035):0,("PV","CO2",2035):0,("PV","Water",2035):0,("Heat-pump","H2",2035):0,("Heat-pump","CH4",2035):0,("Heat-pump","Petrol",2035):0,("Heat-pump","CO2",2035):0,("Heat-pump","Water",2035):0,
         ("Gas-boiler","Heat",2050):0.9,#kwh heat/kWh ng
         ("Gas-boiler","CH4",2050):-1,#kwh ng consumed
         ("PEMFC","Elec",2050):19.98,#c/kg h2
         ("PEMFC","Heat",2050):9.99,#heat/kg h2
         ("PEMFC","H2",2050):-1,#h2 consumed
         ("PEME","H2",2050):0.021,#kg h2/kWh elec
         ("PEME","Elec",2050):-1.05,#kwh elec consumed
         ("PEME","Water",2050):-0.21,
         ("Methanation","CH4",2050):26.307, #kwh CH4/kg H2
         ("Methanation","H2",2050):-1,#kg h2
         ("Methanation","CO2",2050):-5.2,#kg hydrogen
         ("Methanation","Elec",2050):-2.6307,
         ("Methanation","Heat",2050):1.998,#heat methanation
         ("PV","Elec",2050):0.21,
         ("Heat-pump","Elec",2050):-1,#
         ("Heat-pump","Heat",2050):4,#
         ("Gas-boiler","Elec",2050):0,("Gas-boiler","H2",2050):0,("Gas-boiler","Petrol",2050):0,("Gas-boiler","CO2",2050):0,("Gas-boiler","Water",2050):0,("PEMFC","CH4",2050):0,("PEMFC","Petrol",2050):0,
         ("PEMFC","CO2",2050):0,("PEMFC","Water",2050):0,("PEME","Heat",2050):0,("PEME","CH4",2050):0,("PEME","Petrol",2050):0,("PEME","CO2",2050):0,("Methanation","Petrol",2050):0,("Methanation","Water",2050):0,("PV","Heat",2050):0,("PV","H2",2050):0,
         ("PV","CH4",2050):0,("PV","Petrol",2050):0,("PV","CO2",2050):0,("PV","Water",2050):0,("Heat-pump","H2",2050):0,("Heat-pump","CH4",2050):0,("Heat-pump","Petrol",2050):0,("Heat-pump","CO2",2050):0,("Heat-pump","Water",2050):0}#you can add heat for electrolyser

    MPL={"PV":0,"PEMFC":0,"PEME":0,"Gas-boiler":0,"Methanation":0,"Heat-pump":0}#Part load minimum operation #not included yet
    MSU={"PV":1,"PEMFC":0.9,"PEME":0.9,"Gas-boiler":1,"Methanation":0.5,"Heat-pump":1}#Start up,shut down % max capacity in hours switched on and off

    CCost_slope={("PEMFC","Elec",2018):3500,("PEMFC","Heat",2018):0,("PEMFC","H2",2018):0,("PEMFC","CH4",2018):0,("PEMFC","Petrol",2018):0,("PEMFC","CO2",2018):0,("PEMFC","Water",2018):0,
           ("PEME","Elec",2018):0,("PEME","Heat",2018):0,("PEME","H2",2018):42811,("PEME","CH4",2018):0,("PEME","Petrol",2018):0,("PEME","CO2",2018):0,("PEME","Water",2018):0,
           ("Methanation","Elec",2018):0,("Methanation","Heat",2018):0,("Methanation","H2",2018):0,("Methanation","CH4",2018):602.62,("Methanation","Petrol",2018):0,("Methanation","CO2",2018):0,("Methanation","Water",2018):0,
           ("PV","Elec",2018):245.34,("PV","Heat",2018):0,("PV","H2",2018):0,("PV","CH4",2018):0,("PV","Petrol",2018):0,("PV","CO2",2018):0,("PV","Water",2018):0,
           ("Gas-boiler","Elec",2018):0,("Gas-boiler","Heat",2018):607.52,("Gas-boiler","H2",2018):0,("Gas-boiler","CH4",2018):0,("Gas-boiler","Petrol",2018):0,("Gas-boiler","CO2",2018):0,("Gas-boiler","Water",2018):0,
           ("Heat-pump","Elec",2018):0,("Heat-pump","Heat",2018):1335,("Heat-pump","H2",2018):0,("Heat-pump","CH4",2018):0,("Heat-pump","Petrol",2018):0,("Heat-pump","CO2",2018):0,("Heat-pump","Water",2018):0,
           ("PEMFC","Elec",2035):1750,("PEMFC","Heat",2035):0,("PEMFC","H2",2035):0,("PEMFC","CH4",2035):0,("PEMFC","Petrol",2035):0,("PEMFC","CO2",2035):0,("PEMFC","Water",2035):0,
           ("PEME","Elec",2035):0,("PEME","Heat",2035):0,("PEME","H2",2035):29189.31,("PEME","CH4",2035):0,("PEME","Petrol",2035):0,("PEME","CO2",2035):0,("PEME","Water",2035):0,
           ("Methanation","Elec",2035):0,("Methanation","Heat",2035):0,("Methanation","H2",2035):0,("Methanation","CH4",2035):401.75,("Methanation","Petrol",2035):0,("Methanation","CO2",2035):0,("Methanation","Water",2035):0,
           ("PV","Elec",2035):205.964,("PV","Heat",2035):0,("PV","H2",2035):0,("PV","CH4",2035):0,("PV","Petrol,2018",2035):0,("PV","CO2",2035):0,("PV","Water",2035):0,
           ("Gas-boiler","Elec",2035):0,("Gas-boiler","Heat",2035):607.52,("Gas-boiler","H2",2035):0,("Gas-boiler","CH4",2035):0,("Gas-boiler","Petrol",2035):0,("Gas-boiler","CO2",2035):0,("Gas-boiler","Water",2035):0,
           ("Heat-pump","Elec",2035):0,("Heat-pump","Heat",2035):993.125,("Heat-pump","H2",2035):0,("Heat-pump","CH4",2035):0,("Heat-pump","Petrol",2035):0,("Heat-pump","CO2",2035):0,("Heat-pump","Water",2035):0,
           ("PEMFC","Elec",2050):1167,("PEMFC","Heat",2050):0,("PEMFC","H2",2050):0,("PEMFC","CH4",2050):0,("PEMFC","Petrol",2050):0,("PEMFC","CO2",2050):0,("PEMFC","Water",2050):0,
           ("PEME","Elec",2050):0,("PEME","Heat",2050):0,("PEME","H2",2050):14789.25,("PEME","CH4",2050):0,("PEME","Petrol",2050):0,("PEME","CO2",2050):0,("PEME","Water",2050):0,
           ("Methanation","Elec",2050):0,("Methanation","Heat",2050):0,("Methanation","H2",2050):0,("Methanation","CH4",2050):201,("Methanation","Petrol",2050):0,("Methanation","CO2",2050):0,("Methanation","Water",2050):0,
           ("PV","Elec",2050):178.79,("PV","Heat",2035):0,("PV","H2",2050):0,("PV","CH4",2050):0,("PV","Petrol,2018",2050):0,("PV","CO2",2050):0,("PV","Water",2050):0,
           ("Gas-boiler","Elec",2050):0,("Gas-boiler","Heat",2050):607.52,("Gas-boiler","H2",2050):0,("Gas-boiler","CH4",2050):0,("Gas-boiler","Petrol",2050):0,("Gas-boiler","CO2",2050):0,("Gas-boiler","Water",2050):0,
           ("Heat-pump","Elec",2050):0,("Heat-pump","Heat",2050):851,("Heat-pump","H2",2050):0,("Heat-pump","CH4",2050):0,("Heat-pump","Petrol",2050):0,("Heat-pump","CO2",2050):0,("Heat-pump","Water",2050):0}

    CCost_fixed={("PEMFC","Elec",2018):15000,("PEMFC","Heat",2018):0,("PEMFC","H2",2018):0,("PEMFC","CH4",2018):0,("PEMFC","Petrol",2018):0,("PEMFC","CO2",2018):0,("PEMFC","Water",2018):0,
           ("PEME","Elec",2018):0,("PEME","Heat",2018):0,("PEME","H2",2018):278385,("PEME","CH4",2018):0,("PEME","Petrol",2018):0,("PEME","CO2",2018):0,("PEME","Water",2018):0,
           ("Methanation","Elec",2018):0,("Methanation","Heat",2018):0,("Methanation","H2",2018):0,("Methanation","CH4",2018):11212,("Methanation","Petrol",2018):0,("Methanation","CO2",2018):0,("Methanation","Water",2018):0,
           ("PV","Elec",2018):1361,("PV","Heat",2018):0,("PV","H2",2018):0,("PV","CH4",2018):0,("PV","Petrol",2018):0,("PV","CO2",2018):0,("PV","Water",2018):0,
           ("Gas-boiler","Elec",2018):0,("Gas-boiler","Heat",2018):12583,("Gas-boiler","H2",2018):0,("Gas-boiler","CH4",2018):0,("Gas-boiler","Petrol",2018):0,("Gas-boiler","CO2",2018):0,("Gas-boiler","Water",2018):0,
           ("Heat-pump","Elec",2018):0,("Heat-pump","Heat",2018):11000,("Heat-pump","H2",2018):0,("Heat-pump","CH4",2018):0,("Heat-pump","Petrol",2018):0,("Heat-pump","CO2",2018):0,("Heat-pump","Water",2018):0,
           ("PEMFC","Elec",2035):7500,("PEMFC","Heat",2035):0,("PEMFC","H2",2035):0,("PEMFC","CH4",2035):0,("PEMFC","Petrol",2035):0,("PEMFC","CO2",2035):0,("PEMFC","Water",2035):0,
           ("PEME","Elec",2035):0,("PEME","Heat",2035):0,("PEME","H2",2035):189807,("PEME","CH4",2035):0,("PEME","Petrol",2035):0,("PEME","CO2",2035):0,("PEME","Water",2035):0,
           ("Methanation","Elec",2035):0,("Methanation","Heat",2035):0,("Methanation","H2",2035):0,("Methanation","CH4",2035):7475,("Methanation","Petrol",2035):0,("Methanation","CO2",2035):0,("Methanation","Water",2035):0,
           ("PV","Elec",2035):1143,("PV","Heat",2018):0,("PV","H2",2035):0,("PV","CH4",2035):0,("PV","Petrol",2035):0,("PV","CO2",2035):0,("PV","Water",2035):0,
           ("Gas-boiler","Elec",2035):0,("Gas-boiler","Heat",2035):12583,("Gas-boiler","H2",2035):0,("Gas-boiler","CH4",2035):0,("Gas-boiler","Petrol",2035):0,("Gas-boiler","CO2",2035):0,("Gas-boiler","Water",2035):0,
           ("Heat-pump","Elec",2035):0,("Heat-pump","Heat",2035):9625,("Heat-pump","H2",2035):0,("Heat-pump","CH4",2035):0,("Heat-pump","Petrol",2035):0,("Heat-pump","CO2",2035):0,("Heat-pump","Water",2035):0,
           ("PEMFC","Elec",2050):5000,("PEMFC","Heat",2050):0,("PEMFC","H2",2050):0,("PEMFC","CH4",2050):0,("PEMFC","Petrol",2050):0,("PEMFC","CO2",2050):0,("PEMFC","Water",2050):0,
           ("PEME","Elec",2050):0,("PEME","Heat",2050):0,("PEME","H2",2050):96169,("PEME","CH4",2050):0,("PEME","Petrol",2050):0,("PEME","CO2",2050):0,("PEME","Water",2050):0,
           ("Methanation","Elec",2050):0,("Methanation","Heat",2050):0,("Methanation","H2",2050):0,("Methanation","CH4",2050):3737,("Methanation","Petrol",2050):0,("Methanation","CO2",2050):0,("Methanation","Water",2050):0,
           ("PV","Elec",2050):1041,("PV","Heat",2018):0,("PV","H2",2050):0,("PV","CH4",2050):0,("PV","Petrol",2050):0,("PV","CO2",2050):0,("PV","Water",2050):0,
           ("Gas-boiler","Elec",2050):0,("Gas-boiler","Heat",2050):12583,("Gas-boiler","H2",2050):0,("Gas-boiler","CH4",2050):0,("Gas-boiler","Petrol",2050):0,("Gas-boiler","CO2",2050):0,("Gas-boiler","Water",2050):0,
           ("Heat-pump","Elec",2050):0,("Heat-pump","Heat",2050):8250,("Heat-pump","H2",2050):0,("Heat-pump","CH4",2050):0,("Heat-pump","Petrol",2050):0,("Heat-pump","CO2",2050):0,("Heat-pump","Water",2050):0}
    # Variable omv costs per kWh or kg in the case of PEME
    COMV={("PEMFC","Elec"):0.034,("PEMFC","Heat"):0,("PEMFC","H2"):0,("PEMFC","CH4"):0,("PEMFC","Petrol"):0,("PEMFC","CO2"):0,("PEMFC","Water"):0,
           ("PEME","Elec"):0,("PEME","Heat"):0,("PEME","H2"):0.8325,("PEME","CH4"):0,("PEME","Petrol"):0,("PEME","CO2"):0,("PEME","Water"):0,
           ("Methanation","Elec"):0,("Methanation","Heat"):0,("Methanation","H2"):0,("Methanation","CH4"):0,("Methanation","Petrol"):0,("Methanation","CO2"):0,("Methanation","Water"):0,
           ("PV","Elec"):0,("PV","Heat"):0,("PV","H2"):0,("PV","CH4"):0,("PV","Petrol"):0,("PV","CO2"):0,("PV","Water"):0,
           ("Gas-boiler","Elec"):0,("Gas-boiler","Heat"):0,("Gas-boiler","H2"):0,("Gas-boiler","CH4"):0,("Gas-boiler","Petrol"):0,("Gas-boiler","CO2"):0,("Gas-boiler","Water"):0,
           ("Heat-pump","Elec"):0,("Heat-pump","Heat"):0.015,("Heat-pump","H2"):0,("Heat-pump","CH4"):0,("Heat-pump","Petrol"):0,("Heat-pump","CO2"):0,("Heat-pump","Water"):0}
    #Fixed operation costs annualy per kW installed
    COMF={("PEMFC","Elec"):0,("PEMFC","Heat"):0,("PEMFC","H2"):0,("PEMFC","CH4"):0,("PEMFC","Petrol"):0,("PEMFC","CO2"):0,("PEMFC","Water"):0,
           ("PEME","Elec"):0,("PEME","Heat"):0,("PEME","H2"):0,("PEME","CH4"):0,("PEME","Petrol"):0,("PEME","CO2"):0,("PEME","Water"):0,
           ("Methanation","Elec"):0,("Methanation","Heat"):0,("Methanation","H2"):0,("Methanation","CH4"):20,("Methanation","Petrol"):0,("Methanation","CO2"):0,("Methanation","Water"):0,
           ("PV","Elec"):3,("PV","Heat"):0,("PV","H2"):0,("PV","CH4"):0,("PV","Petrol"):0,("PV","CO2"):0,("PV","Water"):0,
           ("Gas-boiler","Elec"):0,("Gas-boiler","Heat"):5,("Gas-boiler","H2"):0,("Gas-boiler","CH4"):0,("Gas-boiler","Petrol"):0,("Gas-boiler","CO2"):0,("Gas-boiler","Water"):0,
           ("Heat-pump","Elec"):0,("Heat-pump","Heat"):0,("Heat-pump","H2"):0,("Heat-pump","CH4"):0,("Heat-pump","Petrol"):0,("Heat-pump","CO2"):0,("Heat-pump","Water"):0}
    VTechyear={}
    PHEVtechyear={}
    BEVtechyear={}
    VTechyear[2018]=["ICEV-g","ICEV-c","PHEV50","BEV200","FCEV"]
    VTechyear[2035]=["ICEV-g","ICEV-c","PHEV50","PHEV100","BEV200","BEV300","FCEV"]
    VTechyear[2050]=["ICEV-g","ICEV-c","PHEV50","PHEV100","PHEV150","BEV200","BEV300","BEV500","FCEV"]
    PHEVtechyear[2018]=["PHEV50"]
    PHEVtechyear[2035]=["PHEV50","PHEV100"]
    PHEVtechyear[2050]=["PHEV50","PHEV100","PHEV150"]
    BEVtechyear[2018]=["BEV200"]
    BEVtechyear[2035]=["BEV200","BEV300"]
    BEVtechyear[2050]=["BEV200","BEV300","BEV500"]
    VCost={("ICEV-g",2018):22285.17,("ICEV-c",2018):26396,("PHEV50",2018):37204,("BEV200",2018):42681,("FCEV",2018):68083,
           ("ICEV-g",2035):22379.6,("ICEV-c",2035):26509,("PHEV50",2035):32011,("PHEV100",2035):34227,("BEV200",2035):32011.33,("BEV300",2035):37788,("FCEV",2035):48158,
          ("ICEV-g",2050):22663,("ICEV-c",2050):26845,("PHEV50",2050):29032,("PHEV100",2050):30875,("PHEV150",2050):31444.7,("BEV200",2050):27200,("BEV300",2050):30415,("BEV500",2050):36260,("FCEV",2050):31444.76}

    VTech_EE={("ICEV-g",2018):6529,("ICEV-c",2018):6871,("PHEV50",2018):8848,("BEV200",2018):8777,("FCEV",2018):10978,
              ("ICEV-g",2035):6104,("ICEV-c",2035):6424,("PHEV50",2035):8826.78,("PHEV100",2035):8216,("BEV200",2035):8513.23,("BEV300",2035):7966.95,("FCEV",2035):9562,
              ("ICEV-g",2050):5467,("ICEV-c",2050):5754,("PHEV50",2050):8692.44,("PHEV100",2050):7969,("PHEV150",2050):7054,("BEV200",2050):8076.06,("BEV300",2050):7272.3,("BEV500",2050):7126,("FCEV",2050):7812}
    #VOMV={"ICEV-g":0.0978,"ICEV-c":0.0978,"PHEV50":0.1236,"PHEV100":0.1236,"PHEV150":0.1236,"BEV200":0.1458,"BEV300":0.1458,"BEV500":0.1458,"FCEV":0.135595}
    VOMV={"ICEV-g":0.03543,"ICEV-c":0.03543,"PHEV50":0.030456,"PHEV100":0.030456,"PHEV150":0.030456,"BEV200":0.023,"BEV300":0.023,"BEV500":0.023,"FCEV":0.02797}
    #Driving cycle set
    DCycle=["Highway","Average","Urban"]
    #Capacity of vehicle energy storage for each type and energy carrier
    Tank={("ICEV-g","Petrol",2018):458.73,#petrol tank ICEV cap
          ("ICEV-c","CH4",2018):446,
          ("BEV200","Elec",2018):41.59,#BEV electric cap
          ("PHEV50","Elec",2018):10.52525,#PHEV elec cap
          ("PHEV50","Petrol",2018):231.74,#phev gas cap
          ("FCEV","H2",2018):5.862,
          ("ICEV-g","Elec",2018):0,("ICEV-g","Heat",2018):0,("ICEV-g","H2",2018):0,("ICEV-g","CH4",2018):0,("ICEV-g","CO2",2018):0,("ICEV-g","Water",2018):0,
          ("ICEV-c","Elec",2018):0,("ICEV-c","Heat",2018):0,("ICEV-c","H2",2018):0,("ICEV-c","Petrol",2018):0,("ICEV-c","CO2",2018):0,("ICEV-c","Water",2018):0,
          ("BEV200","Heat",2018):0,("BEV200","H2",2018):0,("BEV200","CH4",2018):0,("BEV200","Petrol",2018):0,("BEV200","CO2",2018):0,("BEV200","Water",2018):0,
          ("PHEV50","Heat",2018):0,("PHEV50","H2",2018):0,("PHEV50","CH4",2018):0,("PHEV50","CO2",2018):0,("PHEV50","Water",2018):0,
          ("FCEV","Elec",2018):0,("FCEV","Heat",2018):0,("FCEV","CH4",2018):0,("FCEV","Petrol",2018):0,("FCEV","CO2",2018):0,("FCEV","Water",2018):0,
          ("ICEV-g","Petrol",2035):392.7,#petrol tank ICEV cap
          ("ICEV-c","CH4",2035):379,#petrol tank ICEV cap
          ("BEV200","Elec",2035):36.37,#BEV electric cap
          ("BEV300","Elec",2035):57.8,#BEV electric cap
          ("PHEV50","Elec",2035):9.4484,#PHEV elec cap
          ("PHEV50","Petrol",2035):297.3,#phev gas cap
          ("PHEV100","Elec",2035):19.3,#PHEV elec cap
          ("PHEV100","Petrol",2035):297.3,#phev gas cap
          ("FCEV","H2",2035):7.2055,
          ("ICEV-g","Elec",2035):0,("ICEV-g","Heat",2035):0,("ICEV-g","H2",2035):0,("ICEV-g","CH4",2035):0,("ICEV-g","CO2",2035):0,("ICEV-g","Water",2035):0,
          ("ICEV-c","Elec",2035):0,("ICEV-c","Heat",2035):0,("ICEV-c","H2",2035):0,("ICEV-c","Petrol",2035):0,("ICEV-c","CO2",2035):0,("ICEV-c","Water",2035):0,
          ("BEV200","Heat",2035):0,("BEV200","H2",2035):0,("BEV200","CH4",2035):0,("BEV200","Petrol",2035):0,("BEV200","Water",2035):0,("BEV200","CO2",2035):0,
          ("BEV300","Heat",2035):0,("BEV300","H2",2035):0,("BEV300","CH4",2035):0,("BEV300","Petrol",2035):0,("BEV300","Water",2035):0,("BEV300","CO2",2035):0,
          ("PHEV50","Heat",2035):0,("PHEV50","H2",2035):0,("PHEV50","CH4",2035):0,("PHEV50","CO2",2035):0,("PHEV50","Water",2035):0,
          ("PHEV100","Heat",2035):0,("PHEV100","H2",2035):0,("PHEV100","CH4",2035):0,("PHEV100","CO2",2035):0,("PHEV100","Water",2035):0,
          ("FCEV","Elec",2035):0,("FCEV","Heat",2035):0,("FCEV","CH4",2035):0,("FCEV","Petrol",2035):0,("FCEV","CO2",2035):0,("FCEV","Water",2035):0,
          ("ICEV-g","Petrol",2050):327.9611,#petrol tank ICEV cap
          ("ICEV-c","CH4",2050):314,#petrol tank ICEV cap
          ("BEV200","Elec",2050):30.71,#BEV electric cap
          ("BEV300","Elec",2050):47.73,#BEV electric cap
          ("BEV500","Elec",2050):80.26395,#BEV electric cap
          ("PHEV50","Elec",2050):24.66713,#PHEV elec cap
          ("PHEV50","Petrol",2050):240.87,#phev gas cap
          ("PHEV100","Elec",2050):24.66713,#PHEV elec cap
          ("PHEV100","Petrol",2050):240.87,#phev gas cap
          ("PHEV150","Elec",2050):24.66713,#PHEV elec cap
          ("PHEV150","Petrol",2050):240.87,#phev gas cap
          ("FCEV","H2",2050):6.0196,
          ("ICEV-g","Elec",2050):0,("ICEV-g","Heat",2050):0,("ICEV-g","H2",2050):0,("ICEV-g","CH4",2050):0,("ICEV-g","CO2",2050):0,("ICEV-g","Water",2050):0,
          ("ICEV-c","Elec",2050):0,("ICEV-c","Heat",2050):0,("ICEV-c","H2",2050):0,("ICEV-c","Petrol",2050):0,("ICEV-c","CO2",2050):0,("ICEV-c","Water",2050):0,
          ("BEV200","Heat",2050):0,("BEV200","H2",2050):0,("BEV200","CH4",2050):0,("BEV200","Petrol",2050):0,("BEV200","Water",2050):0,("BEV200","CO2",2050):0,
          ("BEV300","Heat",2050):0,("BEV300","H2",2050):0,("BEV300","CH4",2050):0,("BEV300","Petrol",2050):0,("BEV300","Water",2050):0,("BEV300","CO2",2050):0,
          ("BEV500","Heat",2050):0,("BEV500","H2",2050):0,("BEV500","CH4",2050):0,("BEV500","Petrol",2050):0,("BEV500","Water",2050):0,("BEV500","CO2",2050):0,
          ("PHEV50","Heat",2050):0,("PHEV50","H2",2050):0,("PHEV50","CH4",2050):0,("PHEV50","Water",2050):0,("PHEV50","CO2",2050):0,
          ("PHEV100","Heat",2050):0,("PHEV100","H2",2050):0,("PHEV100","CH4",2050):0,("PHEV100","Water",2050):0,("PHEV100","CO2",2050):0,
          ("PHEV150","Heat",2050):0,("PHEV150","H2",2050):0,("PHEV150","CH4",2050):0,("PHEV150","Water",2050):0,("PHEV150","CO2",2050):0,
          ("FCEV","Heat",2050):0,("FCEV","CH4",2050):0,("FCEV","Petrol",2050):0,("FCEV","Water",2050):0,("FCEV","Elec",2050):0,("FCEV","CO2",2050):0}
    #Vehicle efficiency per powertrain, year, and driving cycle
    Eff={("Highway","ICEV-g","Petrol",2018):1.554,#petol tank ICEV
         ("Highway","ICEV-c","CH4",2018):1.5966,#cng tank ICEV
         ("Highway","BEV200","Elec",2018):4.647,#BEV elec eff
         ("Highway","PHEV50","Elec",2018):4.054,#PHEV elec eff
         ("Highway","PHEV50","Petrol",2018):1.4697,#PHEV gas efficiency
         ("Highway","FCEV","H2",2018):76.52,
         ("Highway","ICEV-g","Elec",2018):0,("Highway","ICEV-g","Heat",2018):0,("Highway","ICEV-g","H2",2018):0,("Highway","ICEV-g","CH4",2018):0,("Highway","ICEV-g","Water",2018):0,("Highway","ICEV-g","CO2",2018):0,
         ("Highway","BEV200","Heat",2018):0,("Highway","BEV200","H2",2018):0,("Highway","BEV200","CH4",2018):0,("Highway","BEV200","Petrol",2018):0,("Highway","BEV200","Water",2018):0,("Highway","BEV200","CO2",2018):0,
         ("Highway","ICEV-c","Elec",2018):0,("Highway","ICEV-c","Heat",2018):0,("Highway","ICEV-c","H2",2018):0,("Highway","ICEV-c","Petrol",2018):0,("Highway","ICEV-c","CO2",2018):0,("Highway","ICEV-c","Water",2018):0,
         ("Highway","PHEV50","Heat",2018):0,("Highway","PHEV50","H2",2018):0,("Highway","PHEV50","CH4",2018):0,("Highway","PHEV50","Water",2018):0,("Highway","PHEV50","CO2",2018):0,
         ("Highway","FCEV","Elec",2018):0,("Highway","FCEV","Heat",2018):0,("Highway","FCEV","CH4",2018):0,("Highway","FCEV","Petrol",2018):0,("Highway","FCEV","Water",2018):0,("Highway","FCEV","CO2",2018):0,
         ("Average","ICEV-g","Petrol",2018):1.525941,#petrol tank ICEV
         ("Average","ICEV-c","CH4",2018):1.5696,#cng tank ICEV
         ("Average","BEV200","Elec",2018):4.6471,#BEV elec eff
         ("Average","PHEV50","Elec",2018):4.750482,#PHEV elec eff
         ("Average","PHEV50","Petrol",2018):1.659509,#PHEV gas efficiency
         ("Average","FCEV","H2",2018):85.29,
         ("Average","ICEV-g","Elec",2018):0,("Average","ICEV-g","Heat",2018):0,("Average","ICEV-g","H2",2018):0,("Average","ICEV-g","CH4",2018):0,("Average","ICEV-g","CO2",2018):0,("Average","ICEV-g","Water",2018):0,
         ("Average","BEV200","Heat",2018):0,("Average","BEV200","H2",2018):0,("Average","BEV200","CH4",2018):0,("Average","BEV200","Petrol",2018):0,("Average","BEV200","Water",2018):0,("Average","BEV200","CO2",2018):0,
         ("Average","ICEV-c","Elec",2018):0,("Average","ICEV-c","Heat",2018):0,("Average","ICEV-c","H2",2018):0,("Average","ICEV-c","Petrol",2018):0,("Average","ICEV-c","Water",2018):0,("Average","ICEV-c","CO2",2018):0,
         ("Average","PHEV50","Heat",2018):0,("Average","PHEV50","H2",2018):0,("Average","PHEV50","CH4",2018):0,("Average","PHEV50","Water",2018):0,("Average","PHEV50","CO2",2018):0,
         ("Average","FCEV","Elec",2018):0,("Average","FCEV","Heat",2018):0,("Average","FCEV","CH4",2018):0,("Average","FCEV","Petrol",2018):0,("Average","FCEV","CO2",2018):0,("Average","FCEV","Water",2018):0,
         ("Urban","ICEV-g","Petrol",2018):1.310612,#petrol tank ICEV
         ("Urban","ICEV-c","CH4",2018):1.313,#petrol tank ICEV
         ("Urban","BEV200","Elec",2018):4.5823,#BEV elec eff
         ("Urban","PHEV50","Elec",2018):4.637574,#PHEV elec eff
         ("Urban","PHEV50","Petrol",2018):1.852373,#PHEV gas efficiency
         ("Urban","FCEV","H2",2018):84.98133,
         ("Urban","ICEV-g","Elec",2018):0,("Urban","ICEV-g","Heat",2018):0,("Urban","ICEV-g","H2",2018):0,("Urban","ICEV-g","CH4",2018):0,("Urban","ICEV-g","Water",2018):0,("Urban","ICEV-g","CO2",2018):0,
         ("Urban","ICEV-c","Elec",2018):0,("Urban","ICEV-c","Heat",2018):0,("Urban","ICEV-c","H2",2018):0,("Urban","ICEV-c","Petrol",2018):0,("Urban","ICEV-c","CO2",2018):0,("Urban","ICEV-c","Water",2018):0,
         ("Urban","BEV200","Heat",2018):0,("Urban","BEV200","H2",2018):0,("Urban","BEV200","CH4",2018):0,("Urban","BEV200","Petrol",2018):0,("Urban","BEV200","Water",2018):0,("Urban","BEV200","CO2",2018):0,
         ("Urban","PHEV50","Heat",2018):0,("Urban","PHEV50","H2",2018):0,("Urban","PHEV50","CH4",2018):0,("Urban","PHEV50","Water",2018):0,("Urban","PHEV50","CO2",2018):0,
         ("Urban","FCEV","Elec",2018):0,("Urban","FCEV","Heat",2018):0,("Urban","FCEV","CH4",2018):0,("Urban","FCEV","Petrol",2018):0,("Urban","FCEV","Water",2018):0,("Urban","FCEV","CO2",2018):0,
         ("Highway","ICEV-g","Petrol",2035):1.813,#petol tank ICEV
         ("Highway","ICEV-c","CH4",2035):1.8613,#petol tank ICEV
         ("Highway","BEV200","Elec",2035):3.946175,#BEV elec eff
         ("Highway","BEV300","Elec",2035):4.366,#BEV elec eff
         ("Highway","PHEV50","Elec",2035):4.46665,#PHEV elec eff
         ("Highway","PHEV50","Petrol",2035):1.7483,#PHEV gas efficiency
         ("Highway","PHEV100","Elec",2035):4.395859,#PHEV elec eff
         ("Highway","PHEV100","Petrol",2035):1.719294,#PHEV gas efficiency
         ("Highway","FCEV","H2",2035):86.021,
         ("Highway","ICEV-g","Elec",2035):0,("Highway","ICEV-g","Heat",2035):0,("Highway","ICEV-g","H2",2035):0,("Highway","ICEV-g","CH4",2035):0,("Highway","ICEV-g","Water",2035):0,("Highway","ICEV-g","CO2",2035):0,
         ("Highway","ICEV-c","Elec",2035):0,("Highway","ICEV-c","Heat",2035):0,("Highway","ICEV-c","H2",2035):0,("Highway","ICEV-c","Petrol",2035):0,("Highway","ICEV-c","CO2",2035):0,("Highway","ICEV-c","Water",2035):0,
         ("Highway","BEV200","Heat",2035):0,("Highway","BEV200","H2",2035):0,("Highway","BEV200","CH4",2035):0,("Highway","BEV200","CO2",2035):0,("Highway","BEV200","Petrol",2035):0,("Highway","BEV200","Water",2035):0,
         ("Highway","PHEV50","Heat",2035):0,("Highway","PHEV50","H2",2035):0,("Highway","PHEV50","CH4",2035):0,("Highway","PHEV50","Water",2035):0,("Highway","PHEV50","CO2",2035):0,
         ("Highway","BEV300","Heat",2035):0,("Highway","BEV300","H2",2035):0,("Highway","BEV300","CH4",2035):0,("Highway","BEV300","CO2",2035):0,("Highway","BEV300","Petrol",2035):0,("Highway","BEV300","Water",2035):0,
         ("Highway","PHEV100","Heat",2035):0,("Highway","PHEV100","H2",2035):0,("Highway","PHEV100","CH4",2035):0,("Highway","PHEV100","Water",2035):0,("Highway","PHEV100","CO2",2035):0,
         ("Highway","FCEV","Elec",2035):0,("Highway","FCEV","Heat",2035):0,("Highway","FCEV","CH4",2035):0,("Highway","FCEV","Petrol",2035):0,("Highway","FCEV","CO2",2035):0,("Highway","FCEV","Water",2035):0,
         ("Average","ICEV-g","Petrol",2035):1.7824498,#petrol tank ICEV
         ("Average","ICEV-c","CH4",2035):1.849,#petrol tank ICEV
         ("Average","BEV200","Elec",2035):5.3919,#BEV elec eff
         ("Average","BEV300","Elec",2035):5.1889,#BEV elec eff
         ("Average","PHEV50","Elec",2035):5.29192,#PHEV elec eff
         ("Average","PHEV50","Petrol",2035):2.06637,#PHEV gas efficiency
         ("Average","PHEV100","Elec",2035):5.179977,#PHEV elec eff
         ("Average","PHEV100","Petrol",2035):2.018151,#PHEV gas efficiency
         ("Average","FCEV","H2",2035):97.14765,
         ("Average","ICEV-g","Elec",2035):0,("Average","ICEV-g","Heat",2035):0,("Average","ICEV-g","H2",2035):0,("Average","ICEV-g","CH4",2035):0,("Average","ICEV-g","Water",2035):0,("Average","ICEV-g","CO2",2035):0,
         ("Average","ICEV-c","Elec",2035):0,("Average","ICEV-c","Heat",2035):0,("Average","ICEV-c","H2",2035):0,("Average","ICEV-c","Petrol",2035):0,("Average","ICEV-c","CO2",2035):0,("Average","ICEV-c","Water",2035):0,
         ("Average","BEV200","Heat",2035):0,("Average","BEV200","H2",2035):0,("Average","BEV200","CH4",2035):0,("Average","BEV200","Petrol",2035):0,("Average","BEV200","Water",2035):0,("Average","BEV200","CO2",2035):0,
         ("Average","PHEV50","Heat",2035):0,("Average","PHEV50","H2",2035):0,("Average","PHEV50","CH4",2035):0,("Average","PHEV50","Water",2035):0,("Average","PHEV50","CO2",2035):0,
         ("Average","BEV300","Heat",2035):0,("Average","BEV300","H2",2035):0,("Average","BEV300","CH4",2035):0,("Average","BEV300","Petrol",2035):0,("Average","BEV300","Water",2035):0,("Average","BEV300","CO2",2035):0,
         ("Average","PHEV100","Heat",2035):0,("Average","PHEV100","H2",2035):0,("Average","PHEV100","CH4",2035):0,("Average","PHEV100","Water",2035):0,("Average","PHEV100","CO2",2035):0,
         ("Average","FCEV","Elec",2035):0,("Average","FCEV","Heat",2035):0,("Average","FCEV","CH4",2035):0,("Average","FCEV","Petrol",2035):0,("Average","FCEV","Water",2035):0,("Average","FCEV","CO2",2035):0,
         ("Urban","ICEV-g","Petrol",2035):1.528697,#petrol tank ICEV
         ("Urban","ICEV-c","CH4",2035):1.530,#petrol tank ICEV
         ("Urban","BEV200","Elec",2035):5.44,#BEV elec eff
         ("Urban","BEV300","Elec",2035):5.175,#BEV elec eff
         ("Urban","PHEV50","Elec",2035):5.242875,#PHEV elec eff
         ("Urban","PHEV50","Petrol",2035):2.14567,#PHEV gas efficiency
         ("Urban","PHEV100","Elec",2035):5.112606,#PHEV elec eff
         ("Urban","PHEV100","Petrol",2035):2.145671,#PHEV gas efficiency
         ("Urban","FCEV","H2",2035):97.758,
         ("Urban","ICEV-g","Elec",2035):0,("Urban","ICEV-g","Heat",2035):0,("Urban","ICEV-g","H2",2035):0,("Urban","ICEV-g","CH4",2035):0,("Urban","ICEV-g","CO2",2035):0,("Urban","ICEV-g","Water",2035):0,
         ("Urban","ICEV-c","Elec",2035):0,("Urban","ICEV-c","Heat",2035):0,("Urban","ICEV-c","H2",2035):0,("Urban","ICEV-c","Petrol",2035):0,("Urban","ICEV-c","CO2",2035):0,("Urban","ICEV-c","Water",2035):0,
         ("Urban","BEV200","Heat",2035):0,("Urban","BEV200","H2",2035):0,("Urban","BEV200","CH4",2035):0,("Urban","BEV200","Petrol",2035):0,("Urban","BEV200","CO2",2035):0,("Urban","BEV200","Water",2035):0,
         ("Urban","PHEV50","Heat",2035):0,("Urban","PHEV50","H2",2035):0,("Urban","PHEV50","CH4",2035):0,("Urban","PHEV50","CO2",2035):0,("Urban","PHEV50","Water",2035):0,
         ("Urban","BEV300","Heat",2035):0,("Urban","BEV300","H2",2035):0,("Urban","BEV300","CH4",2035):0,("Urban","BEV300","Petrol",2035):0,("Urban","BEV300","CO2",2035):0,("Urban","BEV300","Water",2035):0,
         ("Urban","PHEV100","Heat",2035):0,("Urban","PHEV100","H2",2035):0,("Urban","PHEV100","CH4",2035):0,("Urban","PHEV100","CO2",2035):0,("Urban","PHEV100","Water",2035):0,
         ("Urban","FCEV","Elec",2035):0,("Urban","FCEV","Heat",2035):0,("Urban","FCEV","CH4",2035):0,("Urban","FCEV","Petrol",2035):0,("Urban","FCEV","CO2",2035):0,("Urban","FCEV","Water",2035):0,
         ("Highway","ICEV-g","Petrol",2050):2.169448,#petol tank ICEV
         ("Highway","ICEV-c","CH4",2050):2.2275,#petol tank ICEV
         ("Highway","BEV200","Elec",2050):5.19855,#BEV elec eff
         ("Highway","BEV300","Elec",2050):5.1595,#BEV elec eff
         ("Highway","BEV500","Elec",2050):5.083085,#BEV elec eff
         ("Highway","PHEV50","Elec",2050):5.179,#PHEV elec eff
         ("Highway","PHEV50","Petrol",2050):2.1506,#PHEV gas efficiency
         ("Highway","PHEV100","Elec",2050):5.134,#PHEV elec eff
         ("Highway","PHEV100","Petrol",2050):2.13136,#PHEV gas efficiency
         ("Highway","PHEV150","Elec",2050):5.090171,#PHEV elec eff
         ("Highway","PHEV150","Petrol",2050):2.112427,#PHEV gas efficiency
         ("Highway","FCEV","H2",2050):10.24185,
         ("Highway","ICEV-g","Elec",2050):0,("Highway","ICEV-g","Heat",2050):0,("Highway","ICEV-g","H2",2050):0,("Highway","ICEV-g","CH4",2050):0,("Highway","ICEV-g","Water",2050):0,("Highway","ICEV-g","CO2",2050):0,
         ("Highway","ICEV-c","Elec",2050):0,("Highway","ICEV-c","Heat",2050):0,("Highway","ICEV-c","H2",2050):0,("Highway","ICEV-c","Petrol",2050):0,("Highway","ICEV-c","CO2",2050):0,("Highway","ICEV-c","Water",2050):0,
         ("Highway","BEV200","Heat",2050):0,("Highway","BEV200","H2",2050):0,("Highway","BEV200","CH4",2050):0,("Highway","BEV200","Petrol",2050):0,("Highway","BEV200","Water",2050):0,("Highway","BEV200","CO2",2050):0,
         ("Highway","PHEV50","Heat",2050):0,("Highway","PHEV50","H2",2050):0,("Highway","PHEV50","CH4",2050):0,("Highway","PHEV50","Water",2050):0,("Highway","PHEV50","CO2",2050):0,
         ("Highway","BEV300","Heat",2050):0,("Highway","BEV300","H2",2050):0,("Highway","BEV300","CH4",2050):0,("Highway","BEV300","Petrol",2050):0,("Highway","BEV300","Water",2050):0,("Highway","BEV300","CO2",2050):0,
         ("Highway","PHEV100","Heat",2050):0,("Highway","PHEV100","H2",2050):0,("Highway","PHEV100","CH4",2050):0,("Highway","PHEV100","Water",2050):0,("Highway","PHEV100","CO2",2050):0,
         ("Highway","BEV500","Heat",2050):0,("Highway","BEV500","H2",2050):0,("Highway","BEV500","CH4",2050):0,("Highway","BEV500","Petrol",2050):0,("Highway","BEV500","Water",2050):0,("Highway","BEV500","CO2",2050):0,
         ("Highway","PHEV150","Heat",2050):0,("Highway","PHEV150","H2",2050):0,("Highway","PHEV150","CH4",2050):0,("Highway","PHEV150","Water",2050):0,("Highway","PHEV150","CO2",2050):0,
         ("Highway","FCEV","Elec",2050):0,("Highway","FCEV","Heat",2050):0,("Highway","FCEV","CH4",2050):0,("Highway","FCEV","Petrol",2050):0,("Highway","FCEV","Water",2050):0,("Highway","FCEV","CO2",2050):0,
         ("Average","ICEV-g","Petrol",2050):2.134399,#petrol tank ICEV
         ("Average","ICEV-c","CH4",2050):2.229,#petrol tank ICEV
         ("Average","BEV200","Elec",2050):6.39787,#BEV elec eff
         ("Average","BEV300","Elec",2050):6.285101,#BEV elec eff
         ("Average","BEV500","Elec",2050):6.069445,#BEV elec eff
         ("Average","PHEV50","Elec",2050):6.2267,#PHEV elec eff
         ("Average","PHEV50","Petrol",2050):2.5558,#PHEV gas efficiency
         ("Average","PHEV100","Elec",2050):6.153,#PHEV elec eff
         ("Average","PHEV100","Petrol",2050):2.523,#PHEV gas efficiency
         ("Average","PHEV150","Elec",2050):6.080967,#PHEV elec eff
         ("Average","PHEV150","Petrol",2050):2.490962,#PHEV gas efficiency
         ("Average","FCEV","H2",2050):116.2863,
         ("Average","ICEV-g","Elec",2050):0,("Average","ICEV-g","Heat",2050):0,("Average","ICEV-g","H2",2050):0,("Average","ICEV-g","CH4",2050):0,("Average","ICEV-g","Water",2050):0,("Average","ICEV-g","CO2",2050):0,
         ("Average","ICEV-c","Elec",2050):0,("Average","ICEV-c","Heat",2050):0,("Average","ICEV-c","H2",2050):0,("Average","ICEV-c","Petrol",2050):0,("Average","ICEV-c","CO2",2050):0,("Average","ICEV-c","Water",2050):0,
         ("Average","BEV200","Heat",2050):0,("Average","BEV200","H2",2050):0,("Average","BEV200","CH4",2050):0,("Average","BEV200","Petrol",2050):0,("Average","BEV200","Water",2050):0,("Average","BEV200","CO2",2050):0,
         ("Average","PHEV50","Heat",2050):0,("Average","PHEV50","H2",2050):0,("Average","PHEV50","CH4",2050):0,("Average","PHEV50","Water",2050):0,("Average","PHEV50","CO2",2050):0,
         ("Average","BEV300","Heat",2050):0,("Average","BEV300","H2",2050):0,("Average","BEV300","CH4",2050):0,("Average","BEV300","Petrol",2050):0,("Average","BEV300","Water",2050):0,("Average","BEV300","CO2",2050):0,
         ("Average","PHEV100","Heat",2050):0,("Average","PHEV100","H2",2050):0,("Average","PHEV100","CH4",2050):0,("Average","PHEV100","Water",2050):0,("Average","PHEV100","CO2",2050):0,
         ("Average","BEV500","Heat",2050):0,("Average","BEV500","H2",2050):0,("Average","BEV500","CH4",2050):0,("Average","BEV500","Petrol",2050):0,("Average","BEV500","Water",2050):0,("Average","BEV500","CO2",2050):0,
         ("Average","PHEV150","Heat",2050):0,("Average","PHEV150","H2",2050):0,("Average","PHEV150","CH4",2050):0,("Average","PHEV150","Water",2050):0,("Average","PHEV150","CO2",2050):0,
         ("Average","FCEV","Elec",2050):0,("Average","FCEV","Heat",2050):0,("Average","FCEV","CH4",2050):0,("Average","FCEV","Petrol",2050):0,("Average","FCEV","CO2",2050):0,("Average","FCEV","Water",2050):0,
         ("Urban","ICEV-g","Petrol",2050):1.806152,#petrol tank ICEV
         ("Urban","ICEV-c","CH4",2050):1.8125,#petrol tank ICEV
         ("Urban","BEV200","Elec",2050):6.63455,#BEV elec eff
         ("Urban","BEV300","Elec",2050):6.44167,#BEV elec eff
         ("Urban","BEV500","Elec",2050):6.0876844,#BEV elec eff
         ("Urban","PHEV50","Elec",2050):6.2785,#PHEV elec eff
         ("Urban","PHEV50","Petrol",2050):2.7154,#PHEV gas efficiency
         ("Urban","PHEV100","Elec",2050):6.1883,#PHEV elec eff
         ("Urban","PHEV100","Petrol",2050):2.668,#PHEV gas efficiency
         ("Urban","PHEV150","Elec",2050):6.100724,#PHEV elec eff
         ("Urban","PHEV150","Petrol",2050):2.622299,#PHEV gas efficiency
         ("Urban","FCEV","H2",2050):116.9234,
         ("Urban","ICEV-g","Elec",2050):0,("Urban","ICEV-g","Heat",2050):0,("Urban","ICEV-g","H2",2050):0,("Urban","ICEV-g","CH4",2050):0,("Urban","ICEV-g","Water",2050):0,("Urban","ICEV-g","CO2",2050):0,
         ("Urban","ICEV-c","Elec",2050):0,("Urban","ICEV-c","Heat",2050):0,("Urban","ICEV-c","H2",2050):0,("Urban","ICEV-c","Petrol",2050):0,("Urban","ICEV-c","CO2",2050):0,("Urban","ICEV-c","Water",2050):0,
         ("Urban","BEV200","Heat",2050):0,("Urban","BEV200","H2",2050):0,("Urban","BEV200","CH4",2050):0,("Urban","BEV200","Petrol",2050):0,("Urban","BEV200","Water",2050):0,("Urban","BEV200","CO2",2050):0,
         ("Urban","PHEV50","Heat",2050):0,("Urban","PHEV50","H2",2050):0,("Urban","PHEV50","CH4",2050):0,("Urban","PHEV50","Water",2050):0,("Urban","PHEV50","CO2",2050):0,
         ("Urban","BEV300","Heat",2050):0,("Urban","BEV300","H2",2050):0,("Urban","BEV300","CH4",2050):0,("Urban","BEV300","Petrol",2050):0,("Urban","BEV300","Water",2050):0,("Urban","BEV300","CO2",2050):0,
         ("Urban","PHEV100","Heat",2050):0,("Urban","PHEV100","H2",2050):0,("Urban","PHEV100","CH4",2050):0,("Urban","PHEV100","Water",2050):0,("Urban","PHEV100","CO2",2050):0,
         ("Urban","BEV500","Heat",2050):0,("Urban","BEV500","H2",2050):0,("Urban","BEV500","CH4",2050):0,("Urban","BEV500","Petrol",2050):0,("Urban","BEV500","Water",2050):0,("Urban","BEV500","CO2",2050):0,
         ("Urban","PHEV150","Heat",2050):0,("Urban","PHEV150","H2",2050):0,("Urban","PHEV150","CH4",2050):0,("Urban","PHEV150","Water",2050):0,("Urban","PHEV150","CO2",2050):0,
         ("Urban","FCEV","Elec",2050):0,("Urban","FCEV","Heat",2050):0,("Urban","FCEV","CH4",2050):0,("Urban","FCEV","Petrol",2050):0,("Urban","FCEV","CO2",2050):0,("Urban","FCEV","Water",2050):0,}
    #Maximum vehicle charging limit per hour
    CLim={("ICEV-g","Petrol"):18000,#petrol tank ICEV cap kWh/hour based on 35L gas per min
          ("ICEV-c","CH4"):18000,#petrol tank ICEV cap kWh/hour based on 35L gas per min
          ("BEV200","Elec"):5,#BEV electric cap
          ("PHEV50","Elec"):2,#PHEV elec cap
          ("PHEV50","Petrol"):18000,#phev gas cap
          ("BEV300","Elec"):5,#BEV electric cap
          ("PHEV150","Elec"):2,#PHEV elec cap
          ("PHEV150","Petrol"):18000,#phev gas cap
          ("BEV500","Elec"):5,#BEV electric cap
          ("PHEV100","Elec"):2,#PHEV elec cap
          ("PHEV100","Petrol"):18000,#phev gas cap
          ("FCEV","H2"):12,#kg/hour
          ("ICEV-g","Elec"):0,("ICEV-g","Heat"):0,("ICEV-g","H2"):0,("ICEV-g","CH4"):0,("ICEV-g","Water"):0,("ICEV-g","CO2"):0,
          ("ICEV-c","Elec"):0,("ICEV-c","Heat"):0,("ICEV-c","H2"):0,("ICEV-c","Petrol"):0,("ICEV-c","Water"):0,("ICEV-c","CO2"):0,
          ("BEV200","Heat"):0,("BEV200","H2"):0,("BEV200","CH4"):0,("BEV200","Petrol"):0,("BEV200","Water"):0,("BEV200","CO2"):0,
          ("BEV300","Heat"):0,("BEV300","H2"):0,("BEV300","CH4"):0,("BEV300","Petrol"):0,("BEV300","Water"):0,("BEV300","CO2"):0,
          ("BEV500","Heat"):0,("BEV500","H2"):0,("BEV500","CH4"):0,("BEV500","Petrol"):0,("BEV500","Water"):0,("BEV500","CO2"):0,
          ("PHEV50","Heat"):0,("PHEV50","H2"):0,("PHEV50","CH4"):0,("PHEV50","Water"):0,("PHEV50","CO2"):0,
          ("PHEV100","Heat"):0,("PHEV100","H2"):0,("PHEV100","CH4"):0,("PHEV100","Water"):0,("PHEV100","CO2"):0,
          ("PHEV150","Heat"):0,("PHEV150","H2"):0,("PHEV150","CH4"):0,("PHEV150","Water"):0,("PHEV150","CO2"):0,
          ("FCEV","Heat"):0,("FCEV","CH4"):0,("FCEV","Petrol"):0,("FCEV","Elec"):0,("FCEV","CO2"):0,("FCEV","Water"):0}

    fullhorizon=range(0,8760) #Full horizon for seasonal storage
    horizon=range(0,360) #Typical days horizon
    buildings=range(0,35) #building indices
    AnnuityC=calculate_annuity(discount,ConvTech,LifetimeC) #Conversion technology annuity
    VChargEff={"Elec":0.96,"Heat":0,"H2":0.99,"CH4":0.99,"CO2":1,"Petrol":1,"Water":1}#Vehicle charging efficiency
    NetworkEff={"Elec":0.98,"Heat":0.92,"H2":0.99,"CH4":0.99,"CO2":1,"Petrol":1,"Water":1} #Network efficiency
    return [FuelPrice,FuelSellPrice,FuelCO2,kmdriven,VChargEff,DConvTech,BConvTech,ChargeAvailable,buildings,building2car,BEVtechyear,PHEVtechyear,Power_limit,TotalLimit,SpotPrice,years,Carriers,horizon,fullhorizon,NoStoreCarriers,cars,VTech,ConvTech,StorTech,DCycle,BLoads,annual_conversion,tdays,Areas,VDemandIn,AnnuityV,AnnuityC,AnnuityS,LifetimeV,LifetimeS,LifetimeC,CMatrix,Eff,Tank,CLim,VCost,VOMV,VTech_EE,CCost_slope,CCost_fixed,COMV,COMF,Conv_EE_slope,Conv_EE_fixed,CostS_slope,CostS_fixed,Stor_EE_fixed,Stor_EE_slope,SOMF,ChargEff,DischEff,Decay,MaxCharg,MaxDisch,MaxCapS,MaxCapC,MPL,MSU]


