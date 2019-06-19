import pandas as pd
import os

def calculate_annuity(discount,index,Lifetime):
    Annuity={}
    for i in index:
        Annuity[i]=discount/(1-(1/((1+discount)**Lifetime[i])))
    return Annuity

root=r'D:/Portia/Mobility/Solothurn/' #Root directory of files
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