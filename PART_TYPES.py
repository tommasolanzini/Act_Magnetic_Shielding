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

def get_binned_data(data, bins):
    """Calculates histogram counts and logarithmic bin centers."""
    counts, bin_edges = np.histogram(data, bins=bins)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    return bin_centers, counts

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

    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    tot_edep = df['Total_Edep_MeV'].sum()
    if tot_edep == 0:
        print("No energy deposited in this simulation.")
        return

    p_electron = df['Electron_Edep_MeV'].sum()
    p_proton = df['Proton_Edep_MeV'].sum()
    p_secondary = df['Secondary_Edep_MeV'].sum()
    p_unclassified = tot_edep - (p_electron + p_proton + p_secondary)
    p_unclassified = max(p_unclassified, 0.0)

    # < 10 MeV breakdown
    df_under_10 = df[df['Ekin_MeV'] < 10.0]
    u10_tot = df_under_10['Total_Edep_MeV'].sum()
    u10_elec = df_under_10['Electron_Edep_MeV'].sum()
    u10_prot = df_under_10['Proton_Edep_MeV'].sum()
    u10_sec = df_under_10['Secondary_Edep_MeV'].sum()
    u10_unclassified = u10_tot - (u10_elec + u10_prot + u10_sec)
    u10_unclassified = max(u10_unclassified, 0.0)

    categories = [
        'Primary Electrons',
        'Primary Protons',
        'Secondary Particles',
        # 'Other / Unclassified'
    ]
    energies = [p_electron, p_proton, p_secondary, p_unclassified]
    colors = ['#1f77b4', '#d62728', '#2ca02c', '#7f7f7f']
    
    valid_categories = []
    valid_energies = []
    valid_colors = []
    
    for cat, en, col in zip(categories, energies, colors):
        if en > 0:
            valid_categories.append(cat)
            valid_energies.append(en)
            valid_colors.append(col)

    print(f"Total Energy Deposited: {tot_edep:.2e} MeV")
    for cat, en in zip(valid_categories, valid_energies):
        percentage = (en / tot_edep) * 100
        cat_clean = cat.replace('\n', ' ')
        print(f" - {cat_clean}: {en:.2e} MeV ({percentage:.1f}%)")

    print(f"\n--- Breakdown for Incident Particles < 10 MeV ---")
    if u10_tot > 0:
        print(f"Total Deposited (<10 MeV): {u10_tot:.2e} MeV")
        print(f" - Primary Electrons:  {u10_elec:.2e} MeV ({(u10_elec/u10_tot)*100:.1f}%)")
        print(f" - Primary Protons:    {u10_prot:.2e} MeV ({(u10_prot/u10_tot)*100:.1f}%)")
        print(f" - Secondaries:        {u10_sec:.2e} MeV ({(u10_sec/u10_tot)*100:.1f}%)")
        print(f" - Other / Unclassified:{u10_unclassified:.2e} MeV ({(u10_unclassified/u10_tot)*100:.1f}%)")
        print(f" - Sum of categories:   {(u10_elec + u10_prot + u10_sec + u10_unclassified):.2e} MeV (100.0%)")
    else:
        print("No energy deposited by particles < 10 MeV.")

    # ==========================================
    # PLOTTING SECTION
    # ==========================================
    
    # 1. PIE CHART
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax1.pie(
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
    
    fig1.tight_layout()
    fig1.savefig('Particle_Dose_Breakdown.pdf', format='pdf', dpi=300, bbox_inches='tight')

    # 2. LINE PLOT: HITS VS KINETIC ENERGY
    # Isolate kinetic energies based on the deposition source
    mask_primary = (df['Electron_Edep_MeV'] > 0) | (df['Proton_Edep_MeV'] > 0)
    mask_secondary = (df['Secondary_Edep_MeV'] > 0)
    
    ekin_primary = df.loc[mask_primary, 'Ekin_MeV'].values
    ekin_secondary = df.loc[mask_secondary, 'Ekin_MeV'].values
    
    # Define wide logarithmic bins
    e_min = max(df['Ekin_MeV'].min(), 1e-3)
    e_max = max(df['Ekin_MeV'].max(), 1e2)
    bins_log = np.logspace(np.log10(e_min), np.log10(e_max), 15) # 25 bins = wide/large bins

    x_prim, y_prim = get_binned_data(ekin_primary, bins_log)
    x_sec, y_sec = get_binned_data(ekin_secondary, bins_log)

    # Filter out empty bins to keep the line plot continuous on log scale
    valid_p = y_prim > 0
    valid_s = y_sec > 0

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    ax2.plot(x_prim[valid_p], y_prim[valid_p], marker='o', markersize=6,
             linestyle='-', linewidth=2, color='red', label='Primary Hits')
             
    ax2.plot(x_sec[valid_s], y_sec[valid_s], marker='s', markersize=6,
             linestyle='-', linewidth=2, color='green', label='Secondary Hits')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Incident Kinetic Energy (MeV)', fontsize=12)
    ax2.set_ylabel('Number of Hits', fontsize=12)
    
    ax2.grid(True, which="major", ls=":", alpha=0.5, color='gray')
    ax2.legend(fontsize=11)

    fig2.tight_layout()
    # fig2.savefig('Hits_vs_Energy.pdf', format='pdf', dpi=300, bbox_inches='tight')
    
    plt.show()

# EXECUTE
TARGET_CSV = "build/T_sweep/Brem_search/E2_T_10_Al_05_SC.csv"
analyze_particle_contributions(TARGET_CSV)