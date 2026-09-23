import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ACADEMIC STYLE CONFIGURATION
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
    "legend.frameon": True,
    "legend.edgecolor": "black",
    "axes.grid": True
})

def calculate_tid(file_path, sim_particles, flux, days, mass):
    try:
        df = pd.read_csv(file_path, comment='#', names=['Ekin_MeV', 'Edep_MeV'])
        df['Edep_MeV'] = pd.to_numeric(df['Edep_MeV'], errors='coerce')
        df = df.dropna()
        
        energy_joules = df['Edep_MeV'].sum() * 1.602176634e-13
        dose_gy = energy_joules / mass
        
        sphere_area = np.pi * (80.0 ** 2) 
        total_particles = flux * sphere_area * (days * 24 * 3600)
        
        return (dose_gy * (total_particles / sim_particles)) * 0.1 
    except FileNotFoundError:
        return np.nan

# SIMULATION PARAMETERS
MISSION_DAYS = 30 
TARGET_MASS_KG = 0.22834
SIM_PARTICLES = 20000000

# SPENVIS INTEGRAL FLUXES
FLUX_O1_P = 1.4667E+11 # Deep Capture Protons
FLUX_O1_E = 1.2569E+10 # Deep Capture Electrons

FLUX_O2_P = 5.1308E+07 # Outer Orbit Protons
FLUX_O2_E = 3.2429E+08 # Outer Orbit Electrons

THICKNESSES = [0, 1, 3, 5, 10]

# FILE PATHS: Update with actual GEANT4 CSV paths
# Orbit 1 (Deep Capture)
path = "GEANT4_data/build/T_sweep/cubic/"
O1_P_PASS_FILES = [f"{path}P1_T_0_Al_00.csv", f"{path}P1_T_0_Al_01.csv", f"{path}P1_T_0_Al_03.csv", 
                   f"{path}P1_T_0_Al_05.csv", f"{path}P1_T_0_Al_10.csv"]
O1_E_PASS_FILES = [f"{path}E1_T_0_Al_00.csv", f"{path}E1_T_0_Al_01.csv", f"{path}E1_T_0_Al_03.csv", 
                   f"{path}E1_T_0_Al_05.csv", f"{path}E1_T_0_Al_10.csv"]
# O1_P_ACT_FILES = [f"{path}P1_T_1_Al_00.csv", f"{path}P1_T_1_Al_01.csv", f"{path}P1_T_1_Al_03.csv", 
#                   f"{path}P1_T_1_Al_05.csv", f"{path}P1_T_1_Al_10.csv"]
# O1_E_ACT_FILES = [f"{path}E1_T_1_Al_00.csv", f"{path}E1_T_1_Al_01.csv", f"{path}E1_T_1_Al_03.csv", 
#                   f"{path}E1_T_1_Al_05.csv", f"{path}E1_T_1_Al_10.csv"]

# Orbit 2 (Outer Phase)
O2_P_PASS_FILES = [f"{path}P2_T_0_Al_00.csv", f"{path}P2_T_0_Al_01.csv", f"{path}P2_T_0_Al_03.csv", 
                   f"{path}P2_T_0_Al_05.csv", f"{path}P2_T_0_Al_10.csv"]
O2_E_PASS_FILES = [f"{path}E2_T_0_Al_00.csv", f"{path}E2_T_0_Al_01.csv", f"{path}E2_T_0_Al_03.csv", 
                   f"{path}E2_T_0_Al_05.csv", f"{path}E2_T_0_Al_10.csv"]
# O2_P_ACT_FILES = [f"{path}P2_T_1_Al_00.csv", f"{path}P2_T_1_Al_01.csv", f"{path}P2_T_1_Al_03.csv", 
#                    f"{path}P2_T_1_Al_05.csv", f"{path}P2_T_1_Al_10.csv"]
# O2_E_ACT_FILES = [f"{path}E2_T_1_Al_00.csv", f"{path}E2_T_1_Al_01.csv", f"{path}E2_T_1_Al_03.csv", 
#                    f"{path}E2_T_1_Al_05.csv", f"{path}E2_T_1_Al_10.csv"]

# CALCULATE DOSES - ORBIT 1
tid_o1_p_pass = [calculate_tid(f, SIM_PARTICLES, FLUX_O1_P, MISSION_DAYS, TARGET_MASS_KG) for f in O1_P_PASS_FILES]
tid_o1_e_pass = [calculate_tid(f, SIM_PARTICLES, FLUX_O1_E, MISSION_DAYS, TARGET_MASS_KG) for f in O1_E_PASS_FILES]
tid_o1_tot_pass = [p + e for p, e in zip(tid_o1_p_pass, tid_o1_e_pass)]
# Active
# tid_o1_p_act  = [calculate_tid(f, SIM_PARTICLES, FLUX_O1_P, MISSION_DAYS, TARGET_MASS_KG) for f in O1_P_ACT_FILES]
# tid_o1_e_act  = [calculate_tid(f, SIM_PARTICLES, FLUX_O1_E, MISSION_DAYS, TARGET_MASS_KG) for f in O1_E_ACT_FILES]
# tid_o1_tot_act  = [p + e for p, e in zip(tid_o1_p_act, tid_o1_e_act)]

# CALCULATE DOSES - ORBIT 2
tid_o2_p_pass = [calculate_tid(f, SIM_PARTICLES, FLUX_O2_P, MISSION_DAYS, TARGET_MASS_KG) for f in O2_P_PASS_FILES]
tid_o2_e_pass = [calculate_tid(f, SIM_PARTICLES, FLUX_O2_E, MISSION_DAYS, TARGET_MASS_KG) for f in O2_E_PASS_FILES]
tid_o2_tot_pass = [p + e for p, e in zip(tid_o2_p_pass, tid_o2_e_pass)]

# tid_o2_p_act  = [calculate_tid(f, SIM_PARTICLES, FLUX_O2_P, MISSION_DAYS, TARGET_MASS_KG) for f in O2_P_ACT_FILES]
# tid_o2_e_act  = [calculate_tid(f, SIM_PARTICLES, FLUX_O2_E, MISSION_DAYS, TARGET_MASS_KG) for f in O2_E_ACT_FILES]
# tid_o2_tot_act  = [p + e for p, e in zip(tid_o2_p_act, tid_o2_e_act)]

# PLOTTING
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Formatting helpers
def plot_components(ax, th, t_pass, p_pass, e_pass, title, t_act = None, p_act = None, e_act = None):
    # Totals
    ax.plot(th, t_pass, marker='s', markersize=7, color='black', linewidth=1.5, label='Total (Passive)')
    if t_act is not None:
        ax.plot(th, t_act, marker='o', markersize=7, color='#1f77b4', linewidth=1.5, label='Total (Active)')
    # Protons
    ax.plot(th, p_pass, marker='x', markersize=6, color='#d62728', linestyle='--', linewidth=1.2, label='Protons (Passive)')
    if p_act is not None:
        ax.plot(th, p_act, marker='+', markersize=7, color='#d62728', linestyle=':', linewidth=1.2, label='Protons (Active)')
    # Electrons
    ax.plot(th, e_pass, marker='d', markersize=5, color='#2ca02c', linestyle='--', linewidth=1.2, label='Electrons (Passive)')
    if e_act is not None:
        ax.plot(th, e_act, marker='^', markersize=5, color='#2ca02c', linestyle=':', linewidth=1.2, label='Electrons (Active)')
    
    ax.set_title(title, fontsize=14, pad=10)
    ax.set_xlabel('Aluminium Absorber Thickness (mm)', fontsize=12)
    ax.set_ylabel('Dose in Si (krad)', fontsize=12)
    ax.set_yscale('log')
    ax.set_xticks(THICKNESSES)
    ax.legend(fontsize=10)
    ax.grid(axis='both', which='major', linestyle='-', alpha=0.5)
    ax.grid(axis='y', which='minor', linestyle=':', alpha=0.3)

# Subplot 1: Deep Capture Orbit
plot_components(ax1, THICKNESSES, tid_o1_tot_pass, tid_o1_p_pass, tid_o1_e_pass, 'Deep Capture Orbit (Proton-Dominated)')


# Subplot 2: Outer Orbital Phase
plot_components(ax2, THICKNESSES, tid_o2_tot_pass, tid_o2_p_pass, tid_o2_e_pass, 'Outer Orbital Phase (Electron-Dominated)')

fig.tight_layout()
plt.show()