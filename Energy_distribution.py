import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def load_geant4_data(filepath):
    df = pd.read_csv(filepath, comment='#')
    df.columns = df.columns.str.strip()
    
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    if 'Ekin_MeV' in df.columns:
        ekin = df['Ekin_MeV'].values
    else:
        ekin = df.iloc[:, 1].values
        
    if 'Total_Edep_MeV' in df.columns:
        edep = df['Total_Edep_MeV'].values 
    elif 'Edep_MeV' in df.columns:
        edep = df['Edep_MeV'].values        
    else:
        edep = df.iloc[:, 0].values         
        
    return ekin, edep



df_spenvis = pd.read_csv('SPENVIS_data/spenvis_tr_protons.csv')
initial_energies = df_spenvis['Energy'].values
initial_flux = df_spenvis['Flux'].values

ekin_base, edep_base = load_geant4_data('build/T_sweep/stormer_pay/E2_T_00_Al_00.csv')
ekin_pass, edep_pass = load_geant4_data('build/T_sweep/stormer_pay/E2_T_00_Al_05.csv')
ekin_act1, edep_act1 = load_geant4_data('build/T_sweep/Brem_search/E2_T_10_Al_05_SC.csv')
ekin_act2, edep_act2 = load_geant4_data('build/T_sweep/Brem_search/E2_T_20_Al_05_SC.csv')

T_field = 2.0 

E_min = 1e-3
E_max = 1e3
num_bins = 20
bins_log = np.logspace(np.log10(E_min), np.log10(E_max), num_bins)


plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Computer Modern", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.linewidth": 1.2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
    "xtick.minor.width": 0.8,
    "ytick.minor.width": 0.8,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "legend.frameon": False,
    "axes.grid": False
})

c_base = '#262626' 
c_pass = '#C42021' 
c_act1 = '#005BBB' 
c_act2 = '#228B22' 

line_w = 2.0 
m_size = 5 

def get_line_data(data, bins):
    counts, bin_edges = np.histogram(data, bins=bins)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    mask = counts > 0
    return bin_centers[mask], counts[mask]


fig1, ax1 = plt.subplots(figsize=(8, 5))

x_base, y_base = get_line_data(ekin_base, bins_log)
x_pass, y_pass = get_line_data(ekin_pass, bins_log)
x_act1, y_act1 = get_line_data(ekin_act1, bins_log)
x_act2, y_act2 = get_line_data(ekin_act2, bins_log)

ax1.plot(x_base, y_base*100, marker='o', markersize=m_size, linestyle='-', linewidth=line_w, color=c_base, label='Baseline')
ax1.plot(x_pass, y_pass*100, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive (5 mm Al)')
ax1.plot(x_act1, y_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label=f'Active (1 T & 5 mm Al)')
ax1.plot(x_act2, y_act2, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label=f'Active (2 T & 5 mm Al)')

ax1.set_xlabel('Kinetic Energy (MeV)', fontsize=12)
ax1.set_ylabel('Number of Hits (2B e- per simulation)', fontsize=12)

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim(bottom=0.8) 

ax1.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax1.legend(fontsize=11, loc='upper right')

fig1.tight_layout()
plt.show()


fig2, ax2 = plt.subplots(figsize=(8, 5))

x_edep_pass, y_edep_pass = get_line_data(edep_pass, bins_log)
x_edep_act1, y_edep_act1 = get_line_data(edep_act1, bins_log)
x_edep_act2, y_edep_act2 = get_line_data(edep_act2, bins_log)

ax2.plot(x_edep_pass, y_edep_pass*100, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive (5 mm Al)')
ax2.plot(x_edep_act1, y_edep_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label='Active (1 T & 5 mm Al)')
ax2.plot(x_edep_act2, y_edep_act2, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label='Active (2 T & 5 mm Al)')

ax2.set_xlabel('Deposited Energy (MeV)', fontsize=12)
ax2.set_ylabel('Number of Hits (2B e- per simulation)', fontsize=12)

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_ylim(bottom=0.8)

ax2.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax2.legend(fontsize=11, loc='upper left')

fig2.tight_layout()
plt.show()

# TID

def calculate_mission_tid(file_path, simulated_particles, spenvis_flux,
                          mission_duration_days, target_mass_kg, n_batches=10):
    try:
        df = pd.read_csv(file_path, comment="#")
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"Error: '{file_path}' was not found.")
        return None, None

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()

    if 'Total_Edep_MeV' in df.columns:
        edep_col = 'Total_Edep_MeV'
    elif 'Edep_MeV' in df.columns:
        edep_col = 'Edep_MeV'
    else:
        edep_col = df.columns[0]


    if len(df) < n_batches:
        raise ValueError(
            f"Not enough scored entries in '{file_path}' for "
            f"{n_batches} batches."
        )

    # Split sicuro mantenendo il formato DataFrame
    batch_indices = np.array_split(range(len(df)), n_batches)
    batches = [df.iloc[idx] for idx in batch_indices]

    sphere_radius_cm = 80.0
    sphere_area_cm2 = np.pi * sphere_radius_cm**2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = (
        spenvis_flux * sphere_area_cm2 * mission_seconds
    )

    particles_per_batch = simulated_particles / n_batches
    scaling_factor = total_mission_particles / particles_per_batch

    batch_tids_krad = []

    for batch in batches:
        # Somma l'energia depositata usando la colonna rilevata dinamicamente
        energy_joules = (
            batch[edep_col].sum() * 1.602176634e-13
        )

        simulated_dose_gy = energy_joules / target_mass_kg
        mission_tid_gy = simulated_dose_gy * scaling_factor
        batch_tids_krad.append(mission_tid_gy * 0.1)

    batch_tids_krad = np.asarray(batch_tids_krad)

    mean_tid_krad = np.mean(batch_tids_krad)

    if n_batches > 1:
        standard_error_krad = (
            np.std(batch_tids_krad, ddof=1) / np.sqrt(n_batches)
        )
    else:
        standard_error_krad = 0.0

    relative_uncertainty = (
        standard_error_krad / mean_tid_krad
        if mean_tid_krad > 0
        else np.nan
    )

    print(
        f"TID = {mean_tid_krad:.4g} krad, "
        f"MC batch uncertainty = {standard_error_krad:.4g} krad"
    )
    if np.isfinite(relative_uncertainty):
        print(
            f"Relative uncertainty = "
            f"{100.0 * relative_uncertainty:.3f}%"
        )

    return mean_tid_krad, standard_error_krad

PROTON_FLUX = 1.4667E+11
MISSION_DAYS = 30
TARGET_MASS_KG = 0.22834
N_BATCHES = 10
Passive = [calculate_mission_tid(
    'build/T_sweep/stormer_pay/E2_T_00_Al_05.csv', 1e8, PROTON_FLUX,
    MISSION_DAYS, TARGET_MASS_KG, N_BATCHES
)]
tid_p = Passive[0][0]
std_p = Passive[0][1]

Active_noAl = [calculate_mission_tid(
    'build/T_sweep/Brem_search/E2_T_10_Al_05_SC.csv', 2e9, PROTON_FLUX,
    MISSION_DAYS, TARGET_MASS_KG, N_BATCHES
)]
tid_a1 = Active_noAl[0][0]
std_a1 = Active_noAl[0][1]

Active_Al = [calculate_mission_tid(
    'build/T_sweep/Brem_search/E2_T_20_Al_05_SC.csv', 2e9, PROTON_FLUX,
    MISSION_DAYS, TARGET_MASS_KG, N_BATCHES
)]
tid_a2 = Active_Al[0][0]
std_a2 = Active_Al[0][1]

print(f"\nTID Passive: {tid_p:.4g} krad ± {std_p:.4g} krad")
print(f"TID Active (no Al): {tid_a1:.4g} krad ± {std_a1:.4g} krad")
print(f"TID Active (with Al): {tid_a2:.4g} krad ± {std_a2:.4g} krad")