import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ACADEMIC STYLE CONFIGURATION

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Computer Modern", "DejaVu Serif"],
    "axes.linewidth": 1.2,
    "legend.frameon": False,
})

def analyze_particle_contributions(csv_file):
    print(f"\n--- Analyzing Dose Breakdown for: {csv_file} ---")
    
    columns = [
        'Ekin_MeV', 
        'Total_Edep_MeV', 
        'Electron_Edep_MeV', 
        'Proton_Edep_MeV', 
        'Secondary_Edep_MeV'
    ]
    
    try:
        df = pd.read_csv(csv_file, comment='#', names=columns)
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        return

    # --- THE FIX: Force numeric conversion and drop text/NaN rows ---
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    # ----------------------------------------------------------------

    # Sum the deposited energy across the entire simulation
    tot_edep = df['Total_Edep_MeV'].sum()
    if tot_edep == 0:
        print("No energy deposited in this simulation. Shielding was 100% effective.")
        return

    p_electron = df['Electron_Edep_MeV'].sum()
    p_proton = df['Proton_Edep_MeV'].sum()
    p_secondary = df['Secondary_Edep_MeV'].sum()

    # Group data for plotting
    categories = ['Primary Electrons', 'Primary Protons', 'Secondary Particles\n(Bremsstrahlung / Delta Rays)']
    energies = [p_electron, p_proton, p_secondary]
    colors = ['#1f77b4', '#d62728', '#2ca02c'] 
    
    valid_categories = []
    valid_energies = []
    valid_colors = []
    
    for cat, en, col in zip(categories, energies, colors):
        if en > 0:
            valid_categories.append(cat)
            valid_energies.append(en)
            valid_colors.append(col)

    # Print text summary to the console
    print(f"Total Energy Deposited: {tot_edep:.2e} MeV")
    for cat, en in zip(valid_categories, valid_energies):
        percentage = (en / tot_edep) * 100
        print(f" - {cat}: {en:.2e} MeV ({percentage:.1f}%)")

    # ==========================================
    # PLOTTING THE PIE CHART
    # ==========================================
    fig, ax = plt.subplots(figsize=(8, 6))
    
    wedges, texts, autotexts = ax.pie(
        valid_energies, 
        labels=valid_categories, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=valid_colors,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5},
        textprops={'fontsize': 12}
    )
    
    for autotext in autotexts:
        autotext.set_weight('bold')
        autotext.set_color('white')

    # ax.set_title('Payload Dose Contribution by Particle Type', fontsize=15, pad=20, weight='bold')
    
    fig.tight_layout()
    fig.savefig('Particle_Dose_Breakdown.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

# EXECUTE

# Simply point this to any of your newly generated Geant4 CSVs
TARGET_CSV = "GEANT4_data/build/T_sweep/Brem_search/P1_T_20_Al_05_4x.csv" 
analyze_particle_contributions(TARGET_CSV)