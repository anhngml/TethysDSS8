import pandas as pd
from pandas.api.types import is_numeric_dtype
pd.options.mode.copy_on_write = True
from datetime import timedelta

# Calculate DSS1
def dss1_final (input, fromdate, todate, status_callback):
    df = pd.read_csv(input,skiprows=[1],encoding = "UTF-8") # depend on exisitng dss1.csv file   

    if fromdate is None:
        df["Date"] =  pd.to_datetime(df["Date"]) # convert Date field to  
        fromdate = (pd.to_datetime('today')- timedelta(days=1000))
        todate = (pd.to_datetime('today'))

    # df["Date"] =  pd.to_datetime(df["Date"],dayfirst=True).dt.date    
    df['Date'] = pd.to_datetime(df.Date, format='%d/%m/%Y')
    try:
        wqi = df.loc[(df['Date'] >= fromdate) & (df['Date'] <= todate)] # OK on Python
    except: 
        wqi = df.loc[(df['Date'].dt.date >= fromdate) & (df['Date'].dt.date <= todate)] # OK on Streamlit
    # wqi = df
    row_count = len (df)
    # added_column = ['WQI_I', 'WQI_II', 'WQI_III', 'WQI_IV', 'WQI_V', 'WQI']
    i = 0
    steps =6     
    if 'WQI_I' not in df.columns:
        wqi.insert(6, 'WQI_I', None)  
    wqi['WQI_I'] = wqi.apply(dss1_I, axis=1) # axis =1 for row
    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI_I'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label) 

    if 'WQI_II' not in df.columns:
        wqi.insert(7, 'WQI_II', None)  
    wqi['WQI_II'] = wqi.apply(dss1_II, axis=1)
    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI_II'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label) 

    if 'WQI_III' not in df.columns:
        wqi.insert(8, 'WQI_III', None)  
    wqi['WQI_III'] = wqi.apply(dss1_III, axis=1)
    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI_III'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label) 
    
    if 'WQI_IV' not in df.columns:
        wqi.insert(9, 'WQI_IV', None)  
    wqi['WQI_IV'] = wqi.apply(dss1_IV, axis=1)
    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI_IV'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label) 
    
    if 'WQI_V' not in df.columns:
        wqi.insert(10, 'WQI_V', None)  
    wqi['WQI_V'] = wqi.apply(dss1_V, axis=1)
    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI_V'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label) 
    
    if 'WQI' not in df.columns:
        wqi.insert(11, 'WQI', None)     
    wqi['WQI'] = round((wqi['WQI_I']/100)*(wqi['WQI_II']/100)*(wqi['WQI_III']/100)*wqi['WQI_IV'],0)

    if 'WQI_Level' not in df.columns:
        wqi.insert(12, 'WQI_Level', '') 
    wqi['WQI_Level']  = wqi['WQI'].map(dss1_level)

    if 'WQI_Color' not in df.columns:
        wqi.insert(13, 'WQI_Color', '') 
    wqi['WQI_Color']  = wqi['WQI'].map(dss1_color)

    if 'WQI_Weight' not in df.columns:
        wqi.insert(14, 'WQI_Weight', None) 
    wqi['WQI_Weight'] = round((wqi['WQI_I']/100)*(wqi['WQI_II']/100)*(wqi['WQI_III']/100)*(pow((wqi['WQI_IV']**2)*wqi['WQI_V'],1/3)),0)

    if 'WQI_no_V' not in df.columns:
        wqi.insert(15, 'WQI_no_V', None)  
    wqi['WQI_no_V'] = round((wqi['WQI_I']/100)*(wqi['WQI_II']/100)*(wqi['WQI_III']/100)*(pow(wqi['WQI_IV']*wqi['WQI_V'],1/2)),0)

    i+=1
    percent = int((i/steps)*100)
    label = str(i)+ '/'+ str(steps)+ '. Calculate WQI'    
    if status_callback:
        status_callback(percent,label)
    else:
        print(label)     

    # wqi = wqi.iloc[:,0:11]
    return wqi

params_I = pd.DataFrame(
        {
            "<5.5": [5.5,10],
            "5.5": [5.5,50],
            "6": [6,100],
            "8.5": [8.5,100], 
            "9": [9,50],
            ">9": [9,10],

        }
)

params_II = pd.DataFrame(
        {
            "Aldrin": [0.1],
            "BHC": [0.02],
            "Dieldrin": [0.1], 
            "DDTs": [1],
            "Heptachlor": [0.2],
            "Heptachlorepoxide": [0.2]
        }
)


#Assign DSS1 Level
def dss1_level(wqi_value):
    status = ''
    if wqi_value is not None:
        if wqi_value < 10:
            status =  "Ô nhiễm rất nặng"
        elif wqi_value  >= 10 and wqi_value  <= 25:
            status =  "Kém"
        elif wqi_value >= 26 and wqi_value  <= 50:
            status =  "Xấu"
        elif wqi_value >= 51 and wqi_value  <= 75:
            status =  "Trung bình"
        elif wqi_value >= 75 and wqi_value <= 90:
            status =  "Tốt"
        elif wqi_value >= 91 and wqi_value  <= 100:
            status =  "Rất tốt"
    return status

def dss1_color(wqi_value):
    color = ''
    if wqi_value is not None:
        if wqi_value < 10:
            color =  'RGB(126,0,35)'
        elif wqi_value  >= 10 and wqi_value  <= 25:
            color =  'RGB(255,0,0)'
        elif wqi_value >= 26 and wqi_value  <= 50:
            color =  'RGB(255,126,0)'
        elif wqi_value >= 51 and wqi_value  <= 75:
            color =   'RGB(255,255,0)'
        elif wqi_value >= 75 and wqi_value <= 90:
            color = 'RGB(0,228,0)'
        elif wqi_value >= 91 and wqi_value  <= 100:
            color = 'RGB(51,51,255)'
    return color


#Calculate DSS1_I
def dss1_I(row):
    pH = 1
    if (row['pH'] < params_I.iloc[0][0]) or (row['pH'] >params_I.iloc[0][5]): # pH < 5.5 or pH > 9
        pH = params_I.iloc[1][0] # =10
    
    elif  row['pH'] == params_I.iloc[0][1]: #5.5
        pH = params_I.iloc[1][1] # 50
    elif (row['pH'] > params_I.iloc[0][1]) and  (row['pH'] <params_I.iloc[0][2]): # 5.5 < pH < 6        
        pH = params_I.iloc[1][1]+ (params_I.iloc[1][2] - params_I.iloc[1][1])/(params_I.iloc[0][2]-params_I.iloc[0][1])*(row['pH']-params_I.iloc[0][1])
    
    elif (row['pH'] >= params_I.iloc[0][2]) and (row['pH'] <= params_I.iloc[0][3]): # 6 <= pH <= 8.5
        pH = params_I.iloc[1][2] # 100

    elif (row['pH'] > params_I.iloc[0][3]) and  (row['pH'] <params_I.iloc[0][4]):  # 8.5 < pH <9
        pH = params_I.iloc[1][4]+ (params_I.iloc[1][3]-params_I.iloc[1][4])/(params_I.iloc[0][4]-params_I.iloc[0][3])*(params_I.iloc[0][4]-row['pH'])     
    elif row['pH'] == params_I.iloc[0][4]: # =9
        pH = params_I.iloc[1][4] # 50
    return round(pH,2)

def dss1_II(row):
    Aldrin = BHC = Dieldrin = DDTs = Heptachlor = Heptachlorepoxide = 1
    if (row['Aldrin'] <= params_II.iloc[0][0]): # Aldrin <= 0.1
        Aldrin = 100
    else: Aldrin = 10
    
    if (row['BHC'] <= params_II.iloc[0][1]): # Aldrin <= 0.02
        BHC = 100
    else: BHC = 10
    
    if (row['Dieldrin'] <= params_II.iloc[0][2]): # Dieldrin <= 0.1
        Dieldrin = 100
    else: Dieldrin = 10
    
    if (row['DDTs'] <= params_II.iloc[0][3]): # DDTs <= 1.0
        DDTs = 100
    else: DDTs = 10
    
    if (row['Heptachlor'] <= params_II.iloc[0][4]): # Heptachlor <= 0.2
        Heptachlor = 100
    else: Heptachlor = 10
    
    if (row['Heptachlorepoxide'] <= params_II.iloc[0][5]): # Heptachlorepoxide <= 0.2
        Heptachlorepoxide = 100
    else: Heptachlorepoxide = 10
    # result = round((Aldrin + BHC + Dieldrin + DDTs + Heptachlor + Heptachlorepoxide)/6,2)
    result = round((Aldrin*BHC* Dieldrin *DDTs * Heptachlor * Heptachlorepoxide) ** (1/6),2)
    return result

# As,Cd,Pb,Cr6, Cu, Zn, Hg
params_III_As = pd.DataFrame(
        {
            "<=0.01": [0.01,100],
            "0.02": [0.02,75],
            "0.05": [0.05,50], 
            "0.1": [0.1,25],
            ">0.1": [0.1,10] 
        }
)

params_III_Cd = pd.DataFrame(
        {
            "<0.005": [0.005,100],
            "0.005": [0.005,75],
            "0.008": [0.008,50], 
            "0.01": [0.01,25],
            ">=0.1": [0.1,10] 
        }
)


params_III_Pb = pd.DataFrame(
        {
            "<0.02": [0.02,100],
            "0.02": [0.02,75],
            "0.04": [0.04,50], 
            "0.005": [0.05,25],
            ">=0.5": [0.5,10] 
        }
)

params_III_Cr6 = pd.DataFrame(
        {
            "<=0.01": [0.01,100],
            "0.02": [0.02,75],
            "0.04": [0.04,50], 
            "0.05": [0.05,25],
            ">=0.1": [0.1,10] 
        }
)

params_III_Cu = pd.DataFrame(
        {
            "<0.1": [0.1,100],
            "0.2": [0.2,75],
            "0.5": [0.5,50], 
            "1.0": [1.0,25],
            ">=2": [2.0,10] 
        }
)

params_III_Zn = pd.DataFrame(
        {
            "<=0.5": [0.5,100],
            "1": [1.0,75],
            "1.5": [1.5,50], 
            "2.0": [2.0,25],
            ">=3": [3.0,10] 
        }
)

params_III_Hg = pd.DataFrame(
        {
            "<0.001": [0.001,100],
            "0.001": [0.001,75],
            "0.0015": [0.0015,50], 
            "0.002": [0.002,25],
            ">=0.01": [3.0,10] # > 0.1
        }
)


def dss1_III(row):
    #As
    As=Cd=Pb=Cr6=Cu=Zn=Hg = 1
    if row['As'] <= params_III_As.iloc[0][0]: # 0.01
        As = params_III_As.iloc[1][0] # 100    
    elif row['As'] >  params_III_As.iloc[0][0] and  row['As'] < params_III_As.iloc[0][1]: # 0.01 < As  < 0.02
        As = params_III_As.iloc[1][1]+ (params_III_As.iloc[1][0]-params_III_As.iloc[1][1])/(params_III_As.iloc[0][1]-params_III_As.iloc[0][0])*(params_III_As.iloc[0][1]-row['As'])    
    
    elif row['As'] == params_III_As.iloc[0][1]: # 0.02
        As = params_III_As.iloc[1][1] # 75
    elif row['As'] > params_III_As.iloc[0][1] and row['As'] <  params_III_As.iloc[0][2]: # 0.02 < As  < 0.05
        As = params_III_As.iloc[1][2]+ (params_III_As.iloc[1][1]-params_III_As.iloc[1][2])/(params_III_As.iloc[0][2]-params_III_As.iloc[0][1])*(params_III_As.iloc[0][2]-row['As'])    
    
    elif row['As'] == params_III_As.iloc[0][2]: # 0.05
        As = params_III_As.iloc[1][2] # 50
    elif row['As'] > params_III_As.iloc[0][2] and row['As'] <  params_III_As.iloc[0][3]: # 0.05 < As  < 0.1
        As = params_III_As.iloc[1][3]+ (params_III_As.iloc[1][2]-params_III_As.iloc[1][3])/(params_III_As.iloc[0][3]-params_III_As.iloc[0][2])*(params_III_As.iloc[0][3]-row['As'])    

    elif row['As'] == params_III_As.iloc[0][3]: # = 0.1
        As = params_III_As.iloc[1][3] # 25   
    elif (row['As'] > params_III_As.iloc[0][4]): #> 0.1
        As = params_III_As.iloc[1][4] # =10
    
    #Cd
    if row['Cd'] < params_III_Cd.iloc[0][0]: # < 0.005
        Cd = params_III_Cd.iloc[1][0] # 100 

    elif row['Cd'] == params_III_Cd.iloc[0][1]: # == 0.005
        Cd = params_III_Cd.iloc[1][1] # 75
    elif row['Cd'] > params_III_Cd.iloc[0][1] and row['Cd'] <  params_III_Cd.iloc[0][2]: # 0.005 < Cd  < 0.008
        Cd = params_III_Cd.iloc[1][2]+ (params_III_Cd.iloc[1][1]-params_III_Cd.iloc[1][2])/(params_III_Cd.iloc[0][2]-params_III_Cd.iloc[0][1])*(params_III_Cd.iloc[0][2]-row['Cd'])    
    
    elif row['Cd'] == params_III_Cd.iloc[0][2]: # 0.008
        Cd = params_III_Cd.iloc[1][2] # 50
    elif row['Cd'] > params_III_Cd.iloc[0][2] and row['Cd'] <  params_III_Cd.iloc[0][3]: # 0.008 < Cd  < 0.01
        Cd = params_III_Cd.iloc[1][3]+ (params_III_As.iloc[1][2]-params_III_Cd.iloc[1][3])/(params_III_Cd.iloc[0][3]-params_III_Cd.iloc[0][2])*(params_III_Cd.iloc[0][3]-row['Cd'])    

    elif row['Cd'] == params_III_Cd.iloc[0][3]: # = 0.01
        Cd = params_III_Cd.iloc[1][3] # 25   
    elif row['Cd'] > params_III_Cd.iloc[0][3] and row['Cd'] <  params_III_Cd.iloc[0][4]: # 0.01 < Cd  < 0.1
        Cd = params_III_Cd.iloc[1][4]+ (params_III_Cd.iloc[1][3]-params_III_Cd.iloc[1][4])/(params_III_Cd.iloc[0][4]-params_III_Cd.iloc[0][3])*(params_III_Cd.iloc[0][4]-row['Cd'])    


    elif (row['Cd'] >= params_III_Cd.iloc[0][4]): #>= 0.1
        Cd = params_III_Cd.iloc[1][4] # =10    
    
    #Pb
    if row['Pb'] < params_III_Pb.iloc[0][0]: # < 0.02
        Pb = params_III_Pb.iloc[1][0] # 100 

    elif row['Pb'] == params_III_Pb.iloc[0][1]: # == 0.02
        Pb = params_III_Pb.iloc[1][1] # 75
    elif row['Pb'] > params_III_Pb.iloc[0][1] and row['Pb'] <  params_III_Pb.iloc[0][2]: # 0.02 < Pb  < 0.04
        Pb = params_III_Pb.iloc[1][2]+ (params_III_Pb.iloc[1][1]-params_III_Pb.iloc[1][2])/(params_III_Pb.iloc[0][2]-params_III_Pb.iloc[0][1])*(params_III_Pb.iloc[0][2]-row['Pb'])    
    
    elif row['Pb'] == params_III_Pb.iloc[0][2]: # 0.04
        Pb = params_III_Pb.iloc[1][2] # 50
    elif row['Pb'] > params_III_Pb.iloc[0][2] and row['Pb'] <  params_III_Pb.iloc[0][3]: # 0.04 < Pb  < 0.05
        Pb = params_III_Pb.iloc[1][3]+ (params_III_Pb.iloc[1][2]-params_III_Pb.iloc[1][3])/(params_III_Pb.iloc[0][3]-params_III_Pb.iloc[0][2])*(params_III_Pb.iloc[0][3]-row['Pb'])    

    elif row['Pb'] == params_III_Pb.iloc[0][3]: # = 0.05
        Pb = params_III_Pb.iloc[1][3] # 25 
    elif row['Pb'] > params_III_Pb.iloc[0][3] and row['Pb'] <  params_III_Pb.iloc[0][4]: # 0.05 < Cd  < 0.5
        Pb = params_III_Pb.iloc[1][4]+ (params_III_Pb.iloc[1][3]-params_III_Pb.iloc[1][4])/(params_III_Pb.iloc[0][4]-params_III_Pb.iloc[0][3])*(params_III_Pb.iloc[0][4]-row['Pb'])    

    elif (row['Pb'] >= params_III_Pb.iloc[0][4]): #>= 0.5
        Pb = params_III_Pb.iloc[1][4] # =10    


    #Cr6
    if row['Cr6'] <= params_III_Cr6.iloc[0][0]: # <= 0.01
        Cr6 = params_III_Cr6.iloc[1][0] # 100 
    elif row['Cr6'] >  params_III_Cr6.iloc[0][0] and  row['Cr6'] < params_III_Cr6.iloc[0][1]: # 0.01 < Cr6  < 0.02
        Cr6 = params_III_Cr6.iloc[1][1]+ (params_III_Cr6.iloc[1][0]-params_III_Cr6.iloc[1][1])/(params_III_Cr6.iloc[0][1]-params_III_Cr6.iloc[0][0])*(params_III_Cr6.iloc[0][1]-row['Cr6'])    

    elif row['Cr6'] == params_III_Cr6.iloc[0][1]: # == 0.02
        Cr6 = params_III_Cr6.iloc[1][1] # 75
    elif row['Cr6'] > params_III_Cr6.iloc[0][1] and row['Cr6'] <  params_III_Cr6.iloc[0][2]: # 0.02 < Cr6  < 0.04
        Cr6 = params_III_Cr6.iloc[1][2]+ (params_III_Cr6.iloc[1][1]-params_III_Cr6.iloc[1][2])/(params_III_Cr6.iloc[0][2]-params_III_Cr6.iloc[0][1])*(params_III_Cr6.iloc[0][2]-row['Cr6'])    
    
    elif row['Cr6'] == params_III_Cr6.iloc[0][2]: # 0.04
        Cr6 = params_III_Cr6.iloc[1][2] # 50
    elif row['Cr6'] > params_III_Cr6.iloc[0][2] and row['Cr6'] <  params_III_Cr6.iloc[0][3]: # 0.04 < Cr6  < 0.05
        Cr6 = params_III_Cr6.iloc[1][3]+ (params_III_Cr6.iloc[1][2]-params_III_Cr6.iloc[1][3])/(params_III_Cr6.iloc[0][3]-params_III_Cr6.iloc[0][2])*(params_III_Cr6.iloc[0][3]-row['Cr6'])    

    elif row['Cr6'] == params_III_Cr6.iloc[0][3]: # = 0.05
        Cr6 = params_III_Cr6.iloc[1][3] # 25   
    elif row['Cr6'] > params_III_Cr6.iloc[0][3] and row['Cr6'] <  params_III_Cr6.iloc[0][4]: # 0.05 < Cr6  < 0.1
        Cr6 = params_III_Cr6.iloc[1][4]+ (params_III_Cr6.iloc[1][3]-params_III_Cr6.iloc[1][4])/(params_III_Cr6.iloc[0][4]-params_III_Cr6.iloc[0][3])*(params_III_Cr6.iloc[0][4]-row['Cr6'])    

    elif (row['Cr6'] >= params_III_Cr6.iloc[0][4]): #>= 0.1
        Cr6 = params_III_Cr6.iloc[1][4] # =10    

      #Cu
    if row['Cu'] <= params_III_Cu.iloc[0][0]: # <= 0.1
        Cu = params_III_Cu.iloc[1][0] # 100 

    elif row['Cu'] == params_III_Cu.iloc[0][1]: # == 0.2
        Cu = params_III_Cu.iloc[1][1] # 75
    elif row['Cu'] > params_III_Cu.iloc[0][0] and row['Cu'] <  params_III_Cu.iloc[0][1]: # 0.1 < Cu  < 0.2
        Cu = params_III_Cu.iloc[1][1]+ (params_III_Cu.iloc[1][0]-params_III_Cu.iloc[1][1])/(params_III_Cu.iloc[0][1]-params_III_Cu.iloc[0][0])*(params_III_Cu.iloc[0][1]-row['Cu'])    
    
    elif row['Cu'] == params_III_Cu.iloc[0][2]: # == 0.5
        Cu = params_III_Cu.iloc[1][2] # 50
    elif row['Cu'] > params_III_Cu.iloc[0][1] and row['Cu'] <  params_III_Cu.iloc[0][2]: # 0.2 < Cu  < 0.5
        Cu = params_III_Cu.iloc[1][2]+ (params_III_As.iloc[1][1]-params_III_Cu.iloc[1][2])/(params_III_Cu.iloc[0][2]-params_III_Cu.iloc[0][1])*(params_III_Cu.iloc[0][2]-row['Cu'])    

    elif row['Cu'] == params_III_Cu.iloc[0][3]: # = 1.0
        Cu = params_III_Cu.iloc[1][3] # 25  
    elif row['Cu'] > params_III_Cu.iloc[0][2] and row['Cu'] <  params_III_Cu.iloc[0][3]: # 0.5 < Cu  < 1.0
        Cu = params_III_Cu.iloc[1][3]+ (params_III_As.iloc[1][2]-params_III_Cu.iloc[1][3])/(params_III_Cu.iloc[0][3]-params_III_Cu.iloc[0][2])*(params_III_Cu.iloc[0][3]-row['Cu'])    

    elif row['Cu'] > params_III_Cu.iloc[0][3] and row['Cu'] <  params_III_Cu.iloc[0][4]: #1.0 < Cu  < 2.0
        Cu = params_III_Cu.iloc[1][4]+ (params_III_As.iloc[1][3]-params_III_Cu.iloc[1][4])/(params_III_Cu.iloc[0][4]-params_III_Cu.iloc[0][3])*(params_III_Cu.iloc[0][4]-row['Cu'])    

    elif (row['Cu'] >= params_III_Cu.iloc[0][4]): #>= 2.0
        Cu = params_III_Cu.iloc[1][4] # =10    
    
     #Zn
    if row['Zn'] <= params_III_Zn.iloc[0][0]: # <= 0.5
        Zn = params_III_Zn.iloc[1][0] # 100 

    elif row['Zn'] == params_III_Zn.iloc[0][1]: # == 1.0
        Zn = params_III_Zn.iloc[1][1] # 75
    elif row['Zn'] > params_III_Zn.iloc[0][0] and row['Zn'] <  params_III_Zn.iloc[0][1]: # 0.5 < Zn  <1.0
        Zn = params_III_Zn.iloc[1][1]+ (params_III_Zn.iloc[1][0]-params_III_Zn.iloc[1][1])/(params_III_Zn.iloc[0][1]-params_III_Zn.iloc[0][0])*(params_III_Zn.iloc[0][1]-row['Zn'])    
    
    elif row['Zn'] == params_III_Zn.iloc[0][2]: # == 0.5
        Zn = params_III_Zn.iloc[1][2] # 50
    elif row['Zn'] > params_III_Zn.iloc[0][1] and row['Zn'] <  params_III_Zn.iloc[0][2]: # 1.0 < Zn  < 1.5
        Zn = params_III_Zn.iloc[1][2]+ (params_III_As.iloc[1][1]-params_III_Zn.iloc[1][2])/(params_III_Zn.iloc[0][2]-params_III_Zn.iloc[0][1])*(params_III_Zn.iloc[0][2]-row['Zn'])    

    elif row['Zn'] == params_III_Zn.iloc[0][3]: # = 1.0
        Zn = params_III_Zn.iloc[1][3] # 25  
    elif row['Zn'] > params_III_Zn.iloc[0][2] and row['Zn'] <  params_III_Zn.iloc[0][3]: # 1.5 < Zn  < 2.0
        Zn = params_III_Zn.iloc[1][3]+ (params_III_As.iloc[1][2]-params_III_Zn.iloc[1][3])/(params_III_Zn.iloc[0][3]-params_III_Zn.iloc[0][2])*(params_III_Zn.iloc[0][3]-row['Zn'])    

    elif row['Zn'] > params_III_Zn.iloc[0][3] and row['Zn'] <  params_III_Zn.iloc[0][4]: #2.0 < Zn  < 3.0
        Zn = params_III_Zn.iloc[1][4]+ (params_III_As.iloc[1][3]-params_III_Zn.iloc[1][4])/(params_III_Zn.iloc[0][4]-params_III_Zn.iloc[0][3])*(params_III_Zn.iloc[0][4]-row['Zn'])    

    elif (row['Zn'] >= params_III_Zn.iloc[0][4]): #>= 3.0
        Zn = params_III_Zn.iloc[1][4] # =10           

    #Hg
    if row['Hg'] < params_III_Hg.iloc[0][0]: # < 0.001
        Hg = params_III_Hg.iloc[1][0] # 100 

    elif row['Hg'] == params_III_Hg.iloc[0][1]: # == 0.001
        Hg = params_III_Hg.iloc[1][1] # 75
    elif row['Hg'] > params_III_Hg.iloc[0][1] and row['Hg'] <  params_III_Hg.iloc[0][2]: # 0.001 < Hg  < 0.0015
        Hg = params_III_Hg.iloc[1][2]+ (params_III_Hg.iloc[1][1]-params_III_Hg.iloc[1][2])/(params_III_Hg.iloc[0][2]-params_III_Hg.iloc[0][1])*(params_III_Hg.iloc[0][2]-row['Hg'])    
    
    elif row['Hg'] == params_III_Hg.iloc[0][2]: # 0.0015
        Hg = params_III_Hg.iloc[1][2] # 50
    elif row['Hg'] > params_III_Hg.iloc[0][2] and row['Hg'] <  params_III_Hg.iloc[0][3]: # 0.0015 < Hg  < 0.002
        Hg = params_III_Hg.iloc[1][3]+ (params_III_Hg.iloc[1][2]-params_III_Hg.iloc[1][3])/(params_III_Hg.iloc[0][3]-params_III_Hg.iloc[0][2])*(params_III_Hg.iloc[0][3]-row['Hg'])    

    elif row['Hg'] == params_III_Hg.iloc[0][3]: # = 0.002
        Hg = params_III_Hg.iloc[1][3] # 25   
    elif row['Hg'] > params_III_Hg.iloc[0][3] and row['Hg'] <  params_III_Hg.iloc[0][4]: # 0.002 < Hg  < 0.01
        Hg = params_III_Hg.iloc[1][4]+ (params_III_Hg.iloc[1][3]-params_III_Hg.iloc[1][4])/(params_III_Hg.iloc[0][4]-params_III_Hg.iloc[0][3])*(params_III_Hg.iloc[0][4]-row['Hg'])    

    elif (row['Hg'] >= params_III_Hg.iloc[0][4]): #> 0.01
        Hg = params_III_Hg.iloc[1][4] # =10    

    # result = round((As+Cd+Pb+Cr6+Cu+Zn+Hg)/7,2)

    result = round((As*Cd*Pb*Cr6*Cu*Zn*Hg)**(1/7),2)
    return result

params_IV_DO = pd.DataFrame(
        {
            "<20": [20,10],
            "20": [20,25],
            "50": [50,50],
            "75": [75,75], 
            "88": [88,100],
            "112": [112,100],
            "125": [125,75],
            "150": [150,50],
            "200": [200,25],
            ">200": [200,10],
        }
)

params_IV_BOD5 = pd.DataFrame(
        {
            "<=4": [4,100],
            "6": [6,75],
            "15": [15,50], 
            "25": [25,25],
            ">=50": [50,10]
        }
)

params_IV_COD = pd.DataFrame(
        {
            "<=10": [10,100],
            "15": [15,75],
            "30": [30,50], 
            "50": [50,25],
            ">=150": [150,10]
        }
)

params_IV_TOC = pd.DataFrame(
        {
            "<=4": [4,100],
            "6": [6,75],
            "15": [15,50], 
            "25": [25,25],
            ">=50": [50,10]
        }
)

params_IV_N_NH4 = pd.DataFrame(
        {
            "<=0.3": [0.3,100],
            "0.3": [0.3,75],
            "0.6": [0.6,50], 
            "0.9": [0.9,25],
            ">=5": [5,10]
        }
)

params_IV_N_NO3 = pd.DataFrame(
        {
            "<=2": [2,100],
            "5": [5,75],
            "10": [10,50], 
            "15": [15,25],
            ">15": [15,10]
        }
)

params_IV_N_NO2 = pd.DataFrame(
        {
            "<=0.05": [0.05,100],
            "None1": [None,75],
            "None2": [None,50], 
            "None3": [None,25],
            ">0.05": [0.05,10]
        }
)

params_IV_P_PO4 = pd.DataFrame(
        {
            "<=0.1": [0.1,100],
            "0.2": [0.2,75],
            "0.3": [0.3,50], 
            "0.5": [0.5,25],
            ">=4": [4,10]
        }
)



def dss1_IV(row):
    try:
        T = row['T']
    except: T = 25
    DO_bh=14.652-0.41022*T+0.0079910*pow(T, 2)-0.000077774*pow(T, 3)
    DO_percent_bh = (row['DO']/ DO_bh)*100
    row['DO'] = DO_percent_bh
    DO = BOD5 = COD = TOC = N_NH4 = N_NO3 = N_NO2 = P_PO4 = 0
    ###########
    ## DO
    ###########
    if row['DO'] < params_IV_DO.iloc[0][0] or row['DO'] > params_IV_DO.iloc[0][9]: # < 20 or > 200
        DO = params_IV_DO.iloc[1][0] #10
    
    elif row['DO'] == params_IV_DO.iloc[0][1]: #20
        DO = params_IV_DO.iloc[1][1] #25
    elif row['DO'] > params_IV_DO.iloc[0][1] and row['DO'] < params_IV_DO.iloc[0][2]: # > 20 & < 50)
        DO = params_IV_DO.iloc[1][1]+ (params_IV_DO.iloc[1][2] - params_IV_DO.iloc[1][1])/(params_IV_DO.iloc[0][2]-params_IV_DO.iloc[0][1])*(row['DO']-params_IV_DO.iloc[0][1])
    
    elif row['DO'] == params_IV_DO.iloc[0][2]: #50
        DO = params_IV_DO.iloc[1][2] #50
    elif row['DO'] > params_IV_DO.iloc[0][2] and row['DO'] < params_IV_DO.iloc[0][3]: # > 50 & < 75)        
        DO = params_IV_DO.iloc[1][2]+ (params_IV_DO.iloc[1][3] - params_IV_DO.iloc[1][2])/(params_IV_DO.iloc[0][3]-params_IV_DO.iloc[0][2])*(row['DO']-params_IV_DO.iloc[0][2])
    
    elif row['DO'] == params_IV_DO.iloc[0][3]: #75
        DO = params_IV_DO.iloc[1][3] #75
    elif row['DO'] > params_IV_DO.iloc[0][3] and row['DO'] < params_IV_DO.iloc[0][4]: # >= 75 & < 88)
        DO = params_IV_DO.iloc[1][3]+ (params_IV_DO.iloc[1][4] - params_IV_DO.iloc[1][3])/(params_IV_DO.iloc[0][4]-params_IV_DO.iloc[0][3])*(row['DO']-params_IV_DO.iloc[0][3])

    elif row['DO'] >= params_IV_DO.iloc[0][4] and row['DO'] <= params_IV_DO.iloc[0][5]: #<= 88 and <=112
        DO = params_IV_DO.iloc[1][4] #100
    
    elif row['DO'] > params_IV_DO.iloc[0][5] and row['DO'] < params_IV_DO.iloc[0][6]: # > 112 and < 125
        DO = params_IV_DO.iloc[1][6]+ (params_IV_DO.iloc[1][5] -  params_IV_DO.iloc[1][6])/(params_IV_DO.iloc[0][6]-params_IV_DO.iloc[0][5])*(params_IV_DO.iloc[0][6]-row['DO'])
    
    elif row['DO'] == params_IV_DO.iloc[0][6]: #125
        DO = params_IV_DO.iloc[1][6] #75
    elif row['DO'] > params_IV_DO.iloc[0][6] and row['DO'] < params_IV_DO.iloc[0][7]: # > 125 and < 150
        DO = params_IV_DO.iloc[1][7]+ (params_IV_DO.iloc[1][6] -  params_IV_DO.iloc[1][7])/(params_IV_DO.iloc[0][7]-params_IV_DO.iloc[0][6])*(params_IV_DO.iloc[0][7]-row['DO'])

    elif row['DO'] == params_IV_DO.iloc[0][7]: # 150
        DO = params_IV_DO.iloc[1][7] #50
    elif row['DO'] > params_IV_DO.iloc[0][7] and row['DO'] <= params_IV_DO.iloc[0][8]: # > 150 and < 200
        DO = params_IV_DO.iloc[1][8]+ (params_IV_DO.iloc[1][7] -  params_IV_DO.iloc[1][8])/(params_IV_DO.iloc[0][8]-params_IV_DO.iloc[0][7])*(params_IV_DO.iloc[0][8]-row['DO'])
    
    elif row['DO'] <= params_IV_DO.iloc[0][8]: # 200
        DO = params_IV_DO.iloc[1][8] #10

    ###########
    ## BOD5
    ########### 
    if row['BOD5'] <=params_IV_BOD5.iloc[0][0]: # <=4
        BOD5 = params_IV_BOD5.iloc[1][0] #100        

    elif row['BOD5'] > params_IV_BOD5.iloc[0][0] and row['BOD5'] < params_IV_BOD5.iloc[0][1]: #>4, <6
        BOD5 = params_IV_BOD5.iloc[1][1]+ (params_IV_BOD5.iloc[1][0] -  params_IV_BOD5.iloc[1][1])/(params_IV_BOD5.iloc[0][1]-params_IV_BOD5.iloc[0][0])*(params_IV_BOD5.iloc[0][1]-row['BOD5'])

    elif row['BOD5'] == params_IV_BOD5.iloc[0][1]: #6
        row['BOD5'] = params_IV_BOD5.iloc[1][1] # 75
    elif row['BOD5'] > params_IV_BOD5.iloc[0][1] and row['BOD5'] < params_IV_BOD5.iloc[0][2]: #>6, <15
        BOD5 = params_IV_BOD5.iloc[1][2]+ (params_IV_BOD5.iloc[1][1] -  params_IV_BOD5.iloc[1][2])/(params_IV_BOD5.iloc[0][2]-params_IV_BOD5.iloc[0][1])*(params_IV_BOD5.iloc[0][2]-row['BOD5'])
    
    elif row['BOD5'] == params_IV_BOD5.iloc[0][2]: #15
        row['BOD5'] = params_IV_BOD5.iloc[1][2] # 50
    elif row['BOD5'] > params_IV_BOD5.iloc[0][2] and row['BOD5'] < params_IV_BOD5.iloc[0][3]: #>15, <25
        BOD5 = params_IV_BOD5.iloc[1][3]+ (params_IV_BOD5.iloc[1][2] -  params_IV_BOD5.iloc[1][3])/(params_IV_BOD5.iloc[0][3]-params_IV_BOD5.iloc[0][2])*(params_IV_BOD5.iloc[0][3]-row['BOD5'])
    
    elif row['BOD5'] == params_IV_BOD5.iloc[0][3]: #25
        row['BOD5'] = params_IV_BOD5.iloc[1][3] # 25
    elif row['BOD5'] > params_IV_BOD5.iloc[0][3] and row['BOD5'] < params_IV_BOD5.iloc[0][4]: #>25, <50
        BOD5 = params_IV_BOD5.iloc[1][4]+ (params_IV_BOD5.iloc[1][3] -  params_IV_BOD5.iloc[1][4])/(params_IV_BOD5.iloc[0][4]-params_IV_BOD5.iloc[0][3])*(params_IV_BOD5.iloc[0][4]-row['BOD5'])
    
    elif row['BOD5'] >= params_IV_BOD5.iloc[0][4]: # >= 50
        BOD5 = params_IV_BOD5.iloc[1][4] # 10

    ###########
    ## COD
    ###########
    if row['COD'] <=params_IV_COD.iloc[0][0]: # <=10
        COD = params_IV_COD.iloc[1][0] #100
   
    elif row['COD'] > params_IV_COD.iloc[0][0] and row['COD'] < params_IV_COD.iloc[0][1]: #>10, <15
        COD = params_IV_COD.iloc[1][1]+ (params_IV_COD.iloc[1][0] -  params_IV_COD.iloc[1][1])/(params_IV_COD.iloc[0][1]-params_IV_COD.iloc[0][0])*(params_IV_COD.iloc[0][1]-row['COD'])

    elif row['COD'] == params_IV_COD.iloc[0][1]: #15
        COD = params_IV_COD.iloc[1][1] #75    
    elif row['COD'] > params_IV_COD.iloc[0][1] and row['COD'] < params_IV_COD.iloc[0][2]: #>15, <=30
        COD = params_IV_COD.iloc[1][2]+ (params_IV_COD.iloc[1][1] -  params_IV_COD.iloc[1][2])/(params_IV_COD.iloc[0][2]-params_IV_COD.iloc[0][1])*(params_IV_COD.iloc[0][2]-row['COD'])
    
    elif row['COD'] == params_IV_COD.iloc[0][2]: #30
        COD = params_IV_COD.iloc[1][2] #50
    elif row['COD'] > params_IV_COD.iloc[0][2] and row['COD'] < params_IV_COD.iloc[0][3]: #>30, <50
        COD = params_IV_COD.iloc[1][3]+ (params_IV_COD.iloc[1][2] -  params_IV_COD.iloc[1][3])/(params_IV_COD.iloc[0][3]-params_IV_COD.iloc[0][2])*(params_IV_COD.iloc[0][3]-row['COD'])
    
    elif row['COD'] == params_IV_COD.iloc[0][3]: #50
        COD = params_IV_COD.iloc[1][3] #25
    elif row['COD'] > params_IV_COD.iloc[0][3] and row['COD'] < params_IV_COD.iloc[0][4]: #>50, <150
        COD = params_IV_COD.iloc[1][4]+ (params_IV_COD.iloc[1][3] -  params_IV_COD.iloc[1][4])/(params_IV_COD.iloc[0][4]-params_IV_COD.iloc[0][3])*(params_IV_COD.iloc[0][4]-row['COD'])

    elif row['COD'] >= params_IV_COD.iloc[0][4]: # >= 150
        COD = params_IV_COD.iloc[1][4] # 10
   
    ###########
    ## TOC
    ###########
    if row['TOC'] <=params_IV_TOC.iloc[0][0]: # <=4
        TOC = params_IV_TOC.iloc[1][0] #100
    elif row['TOC'] > params_IV_TOC.iloc[0][0] and row['TOC'] < params_IV_TOC.iloc[0][1]: #>4, <6
        TOC = params_IV_TOC.iloc[1][1]+ (params_IV_TOC.iloc[1][0] -  params_IV_TOC.iloc[1][1])/(params_IV_TOC.iloc[0][1]-params_IV_TOC.iloc[0][0])*(params_IV_TOC.iloc[0][1]-row['TOC'])
    
    elif row['TOC'] < params_IV_TOC.iloc[0][1]: #6
        TOC = params_IV_TOC.iloc[1][1]#75
    elif row['TOC'] > params_IV_TOC.iloc[0][1] and row['TOC'] < params_IV_TOC.iloc[0][2]: #>6, <15
        TOC = params_IV_TOC.iloc[1][2]+ (params_IV_TOC.iloc[1][1] -  params_IV_TOC.iloc[1][2])/(params_IV_TOC.iloc[0][2]-params_IV_TOC.iloc[0][1])*(params_IV_TOC.iloc[0][2]-row['TOC'])
    
    elif row['TOC'] < params_IV_TOC.iloc[0][2]: #15
        TOC = params_IV_TOC.iloc[1][2]#50
    elif row['TOC'] > params_IV_TOC.iloc[0][2] and row['TOC'] <= params_IV_TOC.iloc[0][3]: #>15, <25
        TOC = params_IV_TOC.iloc[1][3]+ (params_IV_TOC.iloc[1][2] -  params_IV_TOC.iloc[1][3])/(params_IV_TOC.iloc[0][3]-params_IV_TOC.iloc[0][2])*(params_IV_TOC.iloc[0][3]-row['TOC'])
    
    elif row['TOC'] < params_IV_TOC.iloc[0][3]: #25
        TOC = params_IV_TOC.iloc[1][3]#25
    elif row['TOC'] > params_IV_TOC.iloc[0][3] and row['TOC'] < params_IV_TOC.iloc[0][4]: #>25, <50
        TOC = params_IV_TOC.iloc[1][4]+ (params_IV_TOC.iloc[1][3] -  params_IV_TOC.iloc[1][4])/(params_IV_TOC.iloc[0][4]-params_IV_TOC.iloc[0][3])*(params_IV_TOC.iloc[0][4]-row['TOC'])

    elif row['TOC'] >= params_IV_TOC.iloc[0][4]: # >= 50
        TOC = params_IV_TOC.iloc[1][4] # 10

    ###########
    ## N_NH4
    ###########
    if row['N_NH4'] < params_IV_N_NH4.iloc[0][0]: # <0.3
        N_NH4 = params_IV_N_NH4.iloc[1][0] #100   
    
    elif row['N_NH4'] == params_IV_N_NH4.iloc[0][1]: # 0.3
        N_NH4 = params_IV_N_NH4.iloc[1][1] #75
    elif row['N_NH4'] > params_IV_N_NH4.iloc[0][1] and row['N_NH4'] < params_IV_N_NH4.iloc[0][2]: #>0.3, <0.6
        N_NH4 = params_IV_N_NH4.iloc[1][2]+ (params_IV_N_NH4.iloc[1][1] -  params_IV_N_NH4.iloc[1][2])/(params_IV_N_NH4.iloc[0][2]-params_IV_N_NH4.iloc[0][1])*(params_IV_N_NH4.iloc[0][2]-row['N_NH4'])
    
    elif row['N_NH4'] == params_IV_N_NH4.iloc[0][2]: # 0.6
        N_NH4 = params_IV_N_NH4.iloc[1][2] #50
    elif row['N_NH4'] > params_IV_N_NH4.iloc[0][2] and row['N_NH4'] < params_IV_N_NH4.iloc[0][3]: #>0.6, <0.9
        N_NH4 = params_IV_N_NH4.iloc[1][3]+ (params_IV_N_NH4.iloc[1][2] -  params_IV_N_NH4.iloc[1][3])/(params_IV_N_NH4.iloc[0][3]-params_IV_N_NH4.iloc[0][2])*(params_IV_N_NH4.iloc[0][3]-row['N_NH4'])
    
    elif row['N_NH4'] == params_IV_N_NH4.iloc[0][3]: # 0.9
        N_NH4 = params_IV_N_NH4.iloc[1][3] #25
    elif row['N_NH4'] > params_IV_N_NH4.iloc[0][3] and row['N_NH4'] < params_IV_N_NH4.iloc[0][4]: #>0.9, <5
        N_NH4 = params_IV_N_NH4.iloc[1][4]+ (params_IV_N_NH4.iloc[1][3] -  params_IV_N_NH4.iloc[1][4])/(params_IV_N_NH4.iloc[0][4]-params_IV_N_NH4.iloc[0][3])*(params_IV_N_NH4.iloc[0][4]-row['N_NH4'])
    
    elif row['N_NH4'] >= params_IV_N_NH4.iloc[0][4]: # >= 5
        N_NH4 = params_IV_N_NH4.iloc[1][4] # 10
    
    
    ###########
    ## N_NO3
    ###########
    if row['N_NO3'] <=params_IV_N_NO3.iloc[0][0]: # <=2
        N_NO3 = params_IV_N_NO3.iloc[1][0] #100
    
    elif row['N_NO3'] > params_IV_N_NO3.iloc[0][0] and row['N_NO3'] < params_IV_N_NO3.iloc[0][1]: #>2, <5
        N_NO3 = params_IV_N_NO3.iloc[1][1]+ (params_IV_N_NO3.iloc[1][0] -  params_IV_N_NO3.iloc[1][1])/(params_IV_N_NO3.iloc[0][1]-params_IV_N_NO3.iloc[0][0])*(params_IV_N_NO3.iloc[0][1]-row['N_NO3'])

    elif row['N_NO3'] == params_IV_N_NO3.iloc[0][1]: #5
        N_NO3 = params_IV_N_NO3.iloc[1][1] #75
    elif row['N_NO3'] > params_IV_N_NO3.iloc[0][1] and row['N_NO3'] < params_IV_N_NO3.iloc[0][2]: #>5, <10
        N_NO3 = params_IV_N_NO3.iloc[1][2]+ (params_IV_N_NO3.iloc[1][1] -  params_IV_N_NO3.iloc[1][2])/(params_IV_N_NO3.iloc[0][2]-params_IV_N_NO3.iloc[0][1])*(params_IV_N_NO3.iloc[0][2]-row['N_NO3'])
    
    elif row['N_NO3'] == params_IV_N_NO3.iloc[0][2]: #10
        N_NO3 = params_IV_N_NO3.iloc[1][2] #50
    elif row['N_NO3'] > params_IV_N_NO3.iloc[0][2] and row['N_NO3'] < params_IV_N_NO3.iloc[0][3]: #>10, <15
        N_NO3 = params_IV_N_NO3.iloc[1][3]+ (params_IV_N_NO3.iloc[1][2] -  params_IV_N_NO3.iloc[1][3])/(params_IV_N_NO3.iloc[0][3]-params_IV_N_NO3.iloc[0][2])*(params_IV_N_NO3.iloc[0][3]-row['N_NO3'])
    
    elif row['N_NO3'] == params_IV_N_NO3.iloc[0][3]: #15
        N_NO3 = params_IV_N_NO3.iloc[1][3] #25

    elif row['N_NO3'] > params_IV_N_NO3.iloc[0][4]: # > 15
        N_NO3 = params_IV_N_NO3.iloc[1][4] # 10

    ###########
    ## N_NO2
    ###########
    if row['N_NO2'] <=params_IV_N_NO2.iloc[0][0]: # <=0.05
        N_NO2 = params_IV_N_NO2.iloc[1][0] #100
    elif row['N_NO2'] > params_IV_N_NO2.iloc[0][4]: # >0.5
        N_NO2 = params_IV_N_NO2.iloc[1][4] # 10

    ###########
    ## P_PO4
    ###########
    if row['P_PO4'] <=params_IV_P_PO4.iloc[0][0]: # <=0.1
        P_PO4 = params_IV_P_PO4.iloc[1][0] #100
    
    elif row['P_PO4'] > params_IV_P_PO4.iloc[0][0] and row['P_PO4'] < params_IV_P_PO4.iloc[0][1]: #>0.1, <0.2
        P_PO4 = params_IV_P_PO4.iloc[1][1]+ (params_IV_P_PO4.iloc[1][0] -  params_IV_P_PO4.iloc[1][1])/(params_IV_P_PO4.iloc[0][1]-params_IV_P_PO4.iloc[0][0])*(params_IV_P_PO4.iloc[0][1]-row['P_PO4'])

    elif row['P_PO4'] ==params_IV_P_PO4.iloc[0][1]: # 0.2
        P_PO4 = params_IV_P_PO4.iloc[1][1]#75
    elif row['P_PO4'] > params_IV_P_PO4.iloc[0][1] and row['P_PO4'] < params_IV_P_PO4.iloc[0][2]: #>0.2, <0.3
        P_PO4 = params_IV_P_PO4.iloc[1][2]+ (params_IV_P_PO4.iloc[1][1] -  params_IV_P_PO4.iloc[1][2])/(params_IV_P_PO4.iloc[0][2]-params_IV_P_PO4.iloc[0][1])*(params_IV_P_PO4.iloc[0][2]-row['P_PO4'])
    
    elif row['P_PO4'] == params_IV_P_PO4.iloc[0][2]: # 0.3
        P_PO4 = params_IV_P_PO4.iloc[1][2]#50
    elif row['P_PO4'] > params_IV_P_PO4.iloc[0][2] and row['P_PO4'] < params_IV_P_PO4.iloc[0][3]: #>0.3, <0.5
        P_PO4 = params_IV_P_PO4.iloc[1][3]+ (params_IV_P_PO4.iloc[1][2] -  params_IV_P_PO4.iloc[1][3])/(params_IV_P_PO4.iloc[0][3]-params_IV_P_PO4.iloc[0][2])*(params_IV_P_PO4.iloc[0][3]-row['P_PO4'])
    
    elif row['P_PO4'] == params_IV_P_PO4.iloc[0][3]: # 0.5
        P_PO4 = params_IV_P_PO4.iloc[1][3]#25
    elif row['P_PO4'] > params_IV_P_PO4.iloc[0][3] and row['P_PO4'] < params_IV_P_PO4.iloc[0][4]: #>0.5, <4.0
        P_PO4 = params_IV_P_PO4.iloc[1][4]+ (params_IV_P_PO4.iloc[1][3] -  params_IV_P_PO4.iloc[1][4])/(params_IV_P_PO4.iloc[0][4]-params_IV_P_PO4.iloc[0][3])*(params_IV_P_PO4.iloc[0][4]-row['P_PO4'])
    
    elif row['P_PO4'] >= params_IV_P_PO4.iloc[0][4]: # >= 4.0
        P_PO4 = params_IV_P_PO4.iloc[1][4] # 10

    result = round((DO + BOD5 + COD + TOC + N_NH4 + N_NO3 + N_NO2 + P_PO4)/8,2)
    return result

###########
## WQI_5
###########
params_V_Coliform = pd.DataFrame(
        {
            "<=2500": [2.5,100],
            "5000": [5.0,75],
            "7500": [7.5,50], 
            "10000": [10.0,25],
            ">10000": [10.0,10]
        }
)

params_V_Ecoli = pd.DataFrame(
        {
            "<=20": [20,100],
            "50": [50,75],
            "100": [100,50], 
            "200": [200,25],
            ">200": [200,10]
        }
)

def dss1_V(row):
    Coliform=Ecoli= 0
    if row['Coliform'] <= params_V_Coliform.iloc[0][0]: # 2500
        Coliform = params_V_Coliform.iloc[1][0] # 100  

    elif row['Coliform'] >  params_V_Coliform.iloc[0][0] and  row['Coliform'] < params_V_Coliform.iloc[0][1]: # 2500 < Coliform  < 5000
        Coliform = params_V_Coliform.iloc[1][1]+ (params_V_Coliform.iloc[1][0]-params_V_Coliform.iloc[1][1])/(params_V_Coliform.iloc[0][1]-params_V_Coliform.iloc[0][0])*(params_V_Coliform.iloc[0][1]-row['Coliform'])    
    
    elif row['Coliform'] == params_V_Coliform.iloc[0][1]: # 5000
        Coliform = params_V_Coliform.iloc[1][1] # 75   
    elif row['Coliform'] > params_V_Coliform.iloc[0][1] and row['Coliform'] <  params_V_Coliform.iloc[0][2]: # 5000 < Coliform  < 7500
        Coliform = params_V_Coliform.iloc[1][2]+ (params_V_Coliform.iloc[1][1]-params_V_Coliform.iloc[1][2])/(params_V_Coliform.iloc[0][2]-params_V_Coliform.iloc[0][1])*(params_V_Coliform.iloc[0][2]-row['Coliform'])    

    elif row['Coliform'] == params_V_Coliform.iloc[0][2]: # 7500
        Coliform = params_V_Coliform.iloc[1][2] # 50
    elif row['Coliform'] > params_V_Coliform.iloc[0][2] and row['Coliform'] <  params_V_Coliform.iloc[0][3]: # 7500 < Coliform  < 10000
        Coliform = params_V_Coliform.iloc[1][3]+ (params_V_Coliform.iloc[1][2]-params_V_Coliform.iloc[1][3])/(params_V_Coliform.iloc[0][3]-params_V_Coliform.iloc[0][2])*(params_V_Coliform.iloc[0][3]-row['Coliform'])    

    elif row['Coliform'] == params_V_Coliform.iloc[0][3]: # 10000
        Coliform = params_V_Coliform.iloc[1][3] # 25 
    elif row['Coliform'] > params_V_Coliform.iloc[0][4]: # >10000
        Coliform = params_V_Coliform.iloc[1][4] # 10

    # Ecoli
    if row['Ecoli'] <= params_V_Ecoli.iloc[0][0]: # 20
        Ecoli = params_V_Ecoli.iloc[1][0] # 100    

    elif row['Ecoli'] >  params_V_Ecoli.iloc[0][0] and  row['Ecoli'] < params_V_Ecoli.iloc[0][1]: # 20 < Ecoli  < 50
        Ecoli = params_V_Ecoli.iloc[1][1]+ (params_V_Ecoli.iloc[1][0]-params_V_Ecoli.iloc[1][1])/(params_V_Ecoli.iloc[0][1]-params_V_Ecoli.iloc[0][0])*(params_V_Ecoli.iloc[0][1]-row['Ecoli'])    
    
    elif row['Ecoli'] == params_V_Ecoli.iloc[0][1]: # 50
        Ecoli = params_V_Ecoli.iloc[1][1] # 75   
    elif row['Ecoli'] > params_V_Ecoli.iloc[0][1] and row['Ecoli'] <  params_V_Ecoli.iloc[0][2]: # 50 < Ecoli  < 100
        Ecoli = params_V_Ecoli.iloc[1][2]+ (params_V_Ecoli.iloc[1][1]-params_V_Ecoli.iloc[1][2])/(params_V_Ecoli.iloc[0][2]-params_V_Ecoli.iloc[0][1])*(params_V_Ecoli.iloc[0][2]-row['Ecoli'])    

    elif row['Ecoli'] == params_V_Ecoli.iloc[0][2]: # 100
        Ecoli = params_V_Ecoli.iloc[1][2] # 50
    elif row['Ecoli'] > params_V_Ecoli.iloc[0][2] and row['Ecoli'] <  params_V_Ecoli.iloc[0][3]: # 100 < Ecoli  < 200
        Ecoli = params_V_Ecoli.iloc[1][3]+ (params_V_Ecoli.iloc[1][2]-params_V_Ecoli.iloc[1][3])/(params_V_Ecoli.iloc[0][3]-params_V_Ecoli.iloc[0][2])*(params_V_Ecoli.iloc[0][3]-row['Ecoli'])    

    elif row['Ecoli'] == params_V_Ecoli.iloc[0][3]: # 200
        Ecoli = params_V_Ecoli.iloc[1][3] # 25 

    elif row['Ecoli'] > params_V_Ecoli.iloc[0][4]: # >200
        Ecoli = params_V_Ecoli.iloc[1][4] # 10
   
    result = round((Coliform + Ecoli)/2,2)
    return result


