import pandas as pd
import re
import matplotlib.pyplot as plt

#Her defineres de lav produktions perioder som blev fundet i Dataanalyse-2035.ipynb
low_energy = [(805,924),(1290,1409),(1492,1611),(4088,4207),(5425,5544),(6334,6453),(7149,7268),
              (7549,7668),(7758,7877),(8155,8274)]

def plot_energy_transfer_l(df, node, period, EENS_sur):
    """
    plotter import og eksport til node fra dens origin og destinations. Plottet er et bar graph time per time
    Til sidst printes samlede EENS og surplus for perioden
    Denne funktion er beregnet til at køres igennem et for loop der kører over overstående liste low_energy

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som der plottes omkring. Den node hvor man vil undersøge import til og eksport fra
        period (tuple): En periode som er defineret som en tuple (start_hour, end_hour) som de står i low_energy listen
        EENS_sur (DataFrame): DataFrame som indeholder data om EENS og surplus
    """
    period_num = low_energy.index(period) + 1  # variable til at holde styr på periode nummeret
    # vælger de kolloner der er relevante for den givne node
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]

    # vælger de rækker der passer til den givne tidsperiode
    start_hour, end_hour = period
    df_period = df_subset.iloc[start_hour:end_hour+1]
    EENS_sur_periods = EENS_sur.iloc[start_hour:end_hour+1]

    # Udregner import værdierne for hvert origin node
    import_values = pd.DataFrame()
    for col in import_cols:
        node_before = col.split("_to_")[0]
        import_from_node = df_period[col].clip(lower=0)
        import_values[node_before] = import_from_node
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        import_to_node = df_period[col].clip(upper=0) * -1
        import_values[node_after] = import_to_node
    import_values.index = df_period.index

    # Udregner eksport værdierne for hvert destination node
    export_values = pd.DataFrame()
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        export_to_node = df_period[col].clip(lower=0) * -1
        export_values[node_after] = export_to_node
    for col in import_cols:
        node_before = col.split(f"_to_")[0]
        export_from_node = df_period[col].clip(upper=0)
        export_values[node_before] = export_from_node
    export_values.index = df_period.index
    
    # Summerer EENS og surplus kolloner for den valgte node og perioden
    total_EENS = EENS_sur_periods[f"{node}_EENS"].sum()
    total_surplus = EENS_sur_periods[f"{node}_surplus"].sum()

    # Laver et et stacked bar chart af import og eksport værdierne for hvert time
    fig, ax = plt.subplots()
    import_colors = ['#008000', '#0F9D58', '#1E8449', '#2ECC71', '#58D68D', '#7DCEA0', '#A9DF9C'] #grønne farver
    export_colors = ['#FF5733', '#FF6B6B', '#FFA07A', '#FFDAB9', '#DC143C', '#B22222', '#8B0000'] #røde farver
    import_handles = []
    export_handles = []
    for i, node_before in enumerate(import_values.columns):
        import_handle = ax.bar(import_values.index, import_values[node_before], bottom=import_values.iloc[:, :i].sum(axis=1), label=node_before + ' import', color=import_colors[i])
        import_handles.append(import_handle)
    for i, node_after in enumerate(export_values.columns):
        export_handle = ax.bar(export_values.index, export_values[node_after], bottom=export_values.iloc[:, :i].sum(axis=1), label=node_after + ' export', color=export_colors[i])
        export_handles.append(export_handle)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Energy transfer (MWh)')
    ax.set_title(f"Energy import and export (Period {period_num}. ({start_hour} to {end_hour})) for {node}")
    ax.legend(handles=import_handles + export_handles, bbox_to_anchor=(1.025,1.025))
    plt.show()
    print(f'Total surplus: {total_surplus:,.2f}. \nTotal EENS: {total_EENS:,.2f}. ')
    
def plot_energy_transfer(df, node, period, EENS_sur):
    """
    plotter import og eksport til node fra dens origin og destinations. Plottet er et bar graph time per time
    Til sidst printes samlede EENS og surplus for perioden
    Denne funktion er beregnet til at køres for sig selv hvor den passeres en tidsperiode ved period

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som der plottes omkring. Den node hvor man vil undersøge import til og eksport fra
        period (tuple): En periode som er defineret som en tuple (start_hour, end_hour)
        EENS_sur (DataFrame): DataFrame som indeholder data om EENS og surplus
    """
    # vælger de kolloner der er relevante for den givne node
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]

    # vælger de rækker der passer til den givne tidsperiode
    start_hour, end_hour = period
    df_period = df_subset.iloc[start_hour:end_hour+1]
    EENS_sur_periods = EENS_sur.iloc[start_hour:end_hour+1]

    # Udregner import værdierne for hvert origin node
    import_values = pd.DataFrame()
    for col in import_cols:
        node_before = col.split("_to_")[0]
        import_from_node = df_period[col].clip(lower=0)
        import_values[node_before] = import_from_node
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        import_to_node = df_period[col].clip(upper=0) * -1
        import_values[node_after] = import_to_node
    import_values.index = df_period.index

    # Udregner eksport værdierne for hvert destination node
    export_values = pd.DataFrame()
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        export_to_node = df_period[col].clip(lower=0) * -1
        export_values[node_after] = export_to_node
    for col in import_cols:
        node_before = col.split(f"_to_")[0]
        export_from_node = df_period[col].clip(upper=0)
        export_values[node_before] = export_from_node
    export_values.index = df_period.index
    
    # Summerer EENS og surplus kolloner for den valgte node og perioden
    total_EENS = EENS_sur_periods[f"{node}_EENS"].sum()
    total_surplus = EENS_sur_periods[f"{node}_surplus"].sum()

    # Laver et et stacked bar chart af import og eksport værdierne for hvert time
    fig, ax = plt.subplots()
    import_colors = ['#008000', '#0F9D58', '#1E8449', '#2ECC71', '#58D68D', '#7DCEA0', '#A9DF9C'] #grønne farver
    export_colors = ['#FF5733', '#FF6B6B', '#FFA07A', '#FFDAB9', '#DC143C', '#B22222', '#8B0000'] #røde farver
    import_handles = []
    export_handles = []
    for i, node_before in enumerate(import_values.columns):
        import_handle = ax.bar(import_values.index, import_values[node_before], bottom=import_values.iloc[:, :i].sum(axis=1), label=node_before + ' import', color=import_colors[i])
        import_handles.append(import_handle)
    for i, node_after in enumerate(export_values.columns):
        export_handle = ax.bar(export_values.index, export_values[node_after], bottom=export_values.iloc[:, :i].sum(axis=1), label=node_after + ' export', color=export_colors[i])
        export_handles.append(export_handle)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Energy transfer (MWh)')
    ax.set_title(f"Energy import and export ({start_hour} to {end_hour}) for {node}")
    ax.legend(handles=import_handles + export_handles, bbox_to_anchor=(1.025,1.025))
    plt.show()
    print(f'Total surplus: {total_surplus:,.2f}. \nTotal EENS: {total_EENS:,.2f}. ')
    
def print_energy_transfer_l(df, node, period, EENS_sur):
    """
    printer import og eksport til node fra dens origin og destinations summeret over hele perioden.
    Derudover printer den også samlede import og eksport for hele perioden
    Til sidst printes samlede EENS og surplus for perioden
    Denne funktion er beregnet til at køres igennem et for loop der kører over overstående liste low_energy

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som der printes iforhold til. Den node hvor man vil undersøge import til og eksport fra
        period (tuple): En periode som er defineret som en tuple (start_hour, end_hour) som de står i low_energy listen
        EENS_sur (DataFrame): DataFrame som indeholder data om EENS og surplus
    """
    period_num = low_energy.index(period) + 1  # variable til at holde styr på periode nummeret
    # vælger de kolloner der er relevante for den givne node
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]

    # vælger de rækker der passer til den givne tidsperiode
    start_hour, end_hour = period
    df_period = df_subset.iloc[start_hour:end_hour+1]
    EENS_sur_periods = EENS_sur.iloc[start_hour:end_hour+1]

    # Udregner import værdierne for hvert origin node
    import_values = pd.DataFrame()
    for col in import_cols:
        node_before = col.split("_to_")[0]
        import_from_node = df_period[col].clip(lower=0)
        import_values[node_before] = import_from_node
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        import_to_node = df_period[col].clip(upper=0) * -1
        import_values[node_after] = import_to_node
    import_values.index = df_period.index

    # Udregner eksport værdierne for hvert destination node
    export_values = pd.DataFrame()
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        export_to_node = df_period[col].clip(lower=0)
        export_values[node_after] = export_to_node
    for col in import_cols:
        node_before = col.split(f"_to_")[0]
        export_from_node = df_period[col].clip(upper=0) * -1
        export_values[node_before] = export_from_node
    export_values.index = df_period.index
    
    # Summerer EENS og surplus kolloner for den valgte node og perioden
    total_EENS = EENS_sur_periods[f"{node}_EENS"].sum()
    total_surplus = EENS_sur_periods[f"{node}_surplus"].sum()
    
    # Summerer import og eksport over hele perioden
    total_imports = pd.DataFrame({col: [import_values[col].sum()] for col in import_values.columns})
    total_exports = pd.DataFrame({col: [export_values[col].sum()] for col in export_values.columns})
    
    # Holder den samme rækkefølge og reindeksere
    import_order = total_imports.columns.tolist()
    total_imports = total_imports.reindex(columns=import_order)
    total_exports = total_exports.reindex(columns=import_order)
    
    # Summerer over alle origin og destination nodes
    total_imports['Total import'] = total_imports.sum(axis=1)
    total_exports['Total export'] = total_exports.sum(axis=1)


    # Printer i det format jeg ønsker
    print(f'Period {period_num}. ({start_hour} to {end_hour})\n')
    print('Total import')
    for col in total_imports.columns:
        print(f"{col}: {total_imports.at[0, col]:,.3f}")
    print('\nTotal export')
    for col in total_exports.columns:
        print(f"{col}: {total_exports.at[0, col]:,.3f}")
        
    print(f'\nTotal surplus: {total_surplus:,.2f}. \nTotal EENS: {total_EENS:,.2f}. \n\n')
    
def print_energy_transfer(df, node, period, EENS_sur):
    """
    printer import og eksport til node fra dens origin og destinations summeret over hele perioden.
    Derudover printer den også samlede import og eksport for hele perioden
    Til sidst printes samlede EENS og surplus for perioden
    Denne funktion er beregnet til at køres for sig selv hvor den passeres en tidsperiode ved period

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som der printes iforhold til. Den node hvor man vil undersøge import til og eksport fra
        period (tuple): En periode som er defineret som en tuple (start_hour, end_hour)
        EENS_sur (DataFrame): DataFrame som indeholder data om EENS og surplus
    """
    # vælger de kolloner der er relevante for den givne node
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]

    # vælger de rækker der passer til den givne tidsperiode
    start_hour, end_hour = period
    df_period = df_subset.iloc[start_hour:end_hour+1]
    EENS_sur_periods = EENS_sur.iloc[start_hour:end_hour+1]

    # Udregner import værdierne for hvert origin node
    import_values = pd.DataFrame()
    for col in import_cols:
        node_before = col.split("_to_")[0]
        import_from_node = df_period[col].clip(lower=0)
        import_values[node_before] = import_from_node
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        import_to_node = df_period[col].clip(upper=0) * -1
        import_values[node_after] = import_to_node
    import_values.index = df_period.index

    # Udregner eksport værdierne for hvert destination node
    export_values = pd.DataFrame()
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        export_to_node = df_period[col].clip(lower=0)
        export_values[node_after] = export_to_node
    for col in import_cols:
        node_before = col.split(f"_to_")[0]
        export_from_node = df_period[col].clip(upper=0) * -1
        export_values[node_before] = export_from_node
    export_values.index = df_period.index
    
    # Summerer EENS og surplus kolloner for den valgte node og perioden
    total_EENS = EENS_sur_periods[f"{node}_EENS"].sum()
    total_surplus = EENS_sur_periods[f"{node}_surplus"].sum()
    
    # Summerer import og eksport over hele perioden
    total_imports = pd.DataFrame({col: [import_values[col].sum()] for col in import_values.columns})
    total_exports = pd.DataFrame({col: [export_values[col].sum()] for col in export_values.columns})
    
    # Holder den samme rækkefølge og reindeksere
    import_order = total_imports.columns.tolist()
    total_imports = total_imports.reindex(columns=import_order)
    total_exports = total_exports.reindex(columns=import_order)
    
    # Summerer over alle origin og destination nodes
    total_imports['Total import'] = total_imports.sum(axis=1)
    total_exports['Total export'] = total_exports.sum(axis=1)

    # Printer i det format jeg ønsker
    print(f'Period ({start_hour} to {end_hour})\n')
    print('Total import')
    for col in total_imports.columns:
        print(f"{col}: {total_imports.at[0, col]:,.3f}")
    print('\nTotal export')
    for col in total_exports.columns:
        print(f"{col}: {total_exports.at[0, col]:,.3f}")
        
    print(f'\nTotal surplus: {total_surplus:,.2f}. \nTotal EENS: {total_EENS:,.2f}. \n\n')
    
def consecutive_export(df, node, hour_limit, energy_limit):
    """
    Denne funktion finder perioder hvor det samlede antal timer er over hour_limit og hver time har en eksport over energy_limit
    Der findes altså først en time med eksport over energy_limit og så undersøger funktionen om de næste 4 timer (eller flere)
    også har en eksport over energy_limit.
    Derefter printer funktionen hver time i de forskellige perioder.
    Til sidst printes hvor mange perioder som der er.

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som hvor perioder med sammenhængende timer over kritisk værdi skal findes
        hour_limit (int): Grænsen af hvor mange sammenhængende timer som er i en periode altså en periode skal være mindst
        hour_limit lang
        energy_limit (int): Kritisk værdi af eksport. Hvis eksport er over denne værdi så overvejes denne time til at indgå
        i en periode.
    """
    # Finder import og eksport kolloner
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]
    
    # Udregner eksport værdierne for hvert destination node
    export_values = pd.DataFrame()
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        export_to_node = df_subset[col].clip(lower=0)
        export_values[node_after] = export_to_node
    for col in import_cols:
        node_before = col.split(f"_to_")[0]
        export_from_node = df_subset[col].clip(upper=0) * -1
        export_values[node_before] = export_from_node
    export_values.index = df_subset.index
    
    #Summerer nodens eksport
    export_values['Export'] = export_values.sum(axis=1)
    
    #Opretter tomme lister til at indeholde de sammenhængede timer
    consecutive_hours = []
    current_consecutive_hours = []

    #Finder alle sammenhængende timer med mere energi end energy_limit og flere sammenhængende timer end hour_limit.
    for i in range(len(export_values)-1):
        if export_values.iloc[i]['Export'] >= energy_limit:
            current_consecutive_hours.append(export_values.index[i])
            if export_values.iloc[i+1]['Export'] >= energy_limit:
                continue
            else:
                if len(current_consecutive_hours) >= hour_limit:
                    consecutive_hours.append(current_consecutive_hours)
                current_consecutive_hours = []
          
    # Finder hvor mange perioder som opfylder kriterierne
    num_lists = len(consecutive_hours)

    # Printer resultaterne
    for hours in consecutive_hours:
        print(hours)
    print(f"\n Number of periods with consecutive hours of export above {energy_limit}: {num_lists}")      
        
def consecutive_import(df, node, hour_limit, energy_limit):
    """
    Denne funktion finder perioder hvor det samlede antal timer er over hour_limit og hver time har en import over energy_limit
    Der findes altså først en time med import over energy_limit og så undersøger funktionen om de næste 4 timer (eller flere)
    også har en import over energy_limit.
    Derefter printer funktionen hver time i de forskellige perioder.
    Til sidst printes hvor mange perioder som der er.

    Parametere:
        df (DataFrame): DataFrame der indeholder datsættet
        node (str): Den node som hvor perioder med sammenhængende timer over kritisk værdi skal findes
        hour_limit (int): Grænsen af hvor mange sammenhængende timer som er i en periode altså en periode skal være mindst
        hour_limit lang
        energy_limit (int): Kritisk værdi af import. Hvis import er over denne værdi så overvejes denne time til at indgå
        i en periode.
    """
    # Finder import og eksport kolloner
    import_cols = [col for col in df.columns if f"_to_{node}" in col]
    export_cols = [col for col in df.columns if f"{node}_to_" in col]
    all_cols = import_cols + export_cols
    df_subset = df.loc[:, all_cols]
    
    # Udregner import værdierne for hvert origin node
    import_values = pd.DataFrame()
    for col in import_cols:
        node_before = col.split("_to_")[0]
        import_from_node = df_subset[col].clip(lower=0)
        import_values[node_before] = import_from_node
    for col in export_cols:
        node_after = col.split(f"_to_")[1]
        import_to_node = df_subset[col].clip(upper=0) * -1
        import_values[node_after] = import_to_node
    import_values.index = df_subset.index
    
    #Summerer nodens import
    import_values['Import'] = import_values.sum(axis=1)
    
    #Opretter tomme lister til at indeholde de sammenhængede timer
    consecutive_hours = []
    current_consecutive_hours = []

    #Finder alle sammenhængende timer med mere energi end energy_limit og flere sammenhængende timer end hour_limit.
    for i in range(len(import_values)-1):
        if import_values.iloc[i]['Import'] >= energy_limit:
            current_consecutive_hours.append(import_values.index[i])
            if import_values.iloc[i+1]['Import'] >= energy_limit:
                continue
            else:
                if len(current_consecutive_hours) >= hour_limit:
                    consecutive_hours.append(current_consecutive_hours)
                current_consecutive_hours = []
                
    # Finder hvor mange perioder som opfylder kriterierne
    num_lists = len(consecutive_hours)

    # Printer resultaterne
    for hours in consecutive_hours:
        print(hours)
    print(f"\n Number of periods with consecutive hours of import above {energy_limit}: {num_lists}")