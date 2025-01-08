import pandas as pd

# Renommer les colonnes
def data_preparation_0(df):
    for i in df.columns :
      l = i.split("_") 
      if len(l)!=1:
        if len(l)>2:
          i1 = l[1]+l[2]
        else:
          i1 = l[1]
        i1 += "_"+l[0]
        df.rename(columns={i:i1},inplace=True)
    return df
# Reformatage des données
def data_preparation_1(df):
    df["id"] = df.index
    df_long = pd.wide_to_long(df.reset_index(), stubnames=[
       'precipitation', 'tempmean', 'tempmin',
       'tempmax','windspeed','pressure'], i=['DATE'], j='town',sep='_',suffix='.+')
    df_long.reset_index()
    df_long
    df3 = df_long[['precipitation', 'tempmean', 'tempmin',
       'tempmax','windspeed','pressure']]
    df3.reset_index(inplace=True)
    return df3 
# Extraire les caractéristiques de la date  
def extract_date_features(df):
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
    df['year'] = df['DATE'].dt.year
    df['month'] = df['DATE'].dt.month
    df['day'] = df['DATE'].dt.day
    df = df.drop(columns='DATE')
    return df  
# Ajouter les décalages pour les colonnes de température (tempmean et tempmax)
def day_in_Life(df, number):
    for i in range(1, number + 1):
        df[[f"tempmean{i}",f"tempmax{i}"]] = df.groupby(['town'])[["tempmean","tempmax"]].shift(i)
    return df
  