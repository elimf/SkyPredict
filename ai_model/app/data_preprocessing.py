import pandas as pd

def prepare_data(df, number):
    # Renommer les colonnes
    for i in df.columns:
        l = i.split("_")
        if len(l) != 1:
            if len(l) > 2:
                i1 = l[1] + l[2]
            else:
                i1 = l[1]
            i1 += "_" + l[0]
            df.rename(columns={i: i1}, inplace=True)
    
    # Reformatage des données
    df["id"] = df.index
    df_temp = pd.wide_to_long(df.reset_index(), stubnames=['precipitation', 'tempmean', 'tempmin', 'tempmax', 'windspeed', 'pressure'], i=['DATE'], j='town', sep='_', suffix='.+')
    df_temp.reset_index(inplace=True)
    df_final = df_temp[['precipitation', 'tempmean', 'tempmin', 'tempmax', 'windspeed', 'pressure']]
    
    #Extraire les caractéristiques de la date
    df_final['DATE'] = pd.to_datetime(df_final['DATE'], format='%Y%m%d')
    df_final['year'] = df_final['DATE'].dt.year
    df_final['month'] = df_final['DATE'].dt.month
    df_final['day'] = df_final['DATE'].dt.day
    df_final = df_final.drop(columns='DATE')
    
    # Ajouter les décalages pour les colonnes de température (tempmean et tempmax)
    for i in range(1, number + 1):
        df_final[[f"tempmean{i}", f"tempmax{i}"]] = df_final.groupby(['town'])[["tempmean", "tempmax"]].shift(i)
    # Retourner le DataFrame préparé
    return df_final