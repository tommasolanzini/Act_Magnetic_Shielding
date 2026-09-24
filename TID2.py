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
    "legend.frameon": False,
    "axes.grid": False
})

def calculate_mission_tid(file_path, particle_type, simulated_particles, spenvis_flux, mission_duration_days, target_mass_kg):
    print(f"\n--- TID Calculation for {particle_type} ---")
    
    try:
        df = pd.read_csv(file_path, comment='#', names=['Ekin_MeV', 'Edep_MeV'])
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None
        
    df['Ekin_MeV'] = pd.to_numeric(df['Ekin_MeV'], errors='coerce')
    df['Edep_MeV'] = pd.to_numeric(df['Edep_MeV'], errors='coerce')
    df = df.dropna()
    
    # Calculate total energy and its standard deviation (MC error: sqrt(sum of squares))
    edep_joules = df['Edep_MeV'] * 1.602176634e-13
    total_energy_joules = edep_joules.sum()
    std_energy_joules = np.sqrt((edep_joules**2).sum())
    
    print(f"Simulated Hits: {len(df)}")
    print(f"Total Energy Deposited: {df['Edep_MeV'].sum():.2e} MeV")
    
    simulated_dose_gy = total_energy_joules / target_mass_kg
    std_simulated_dose_gy = std_energy_joules / target_mass_kg
    
    # Mission Environment Scaling (80 cm spawning sphere)
    sphere_radius_cm = 80.0 
    sphere_area_cm2 = np.pi * (sphere_radius_cm ** 2) 
    
    particles_per_second = spenvis_flux * sphere_area_cm2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = particles_per_second * mission_seconds
    
    scaling_factor = total_mission_particles / simulated_particles
    
    mission_tid_gy = simulated_dose_gy * scaling_factor
    std_mission_tid_gy = std_simulated_dose_gy * scaling_factor
    
    mission_tid_krad = mission_tid_gy * 0.1 
    std_mission_tid_krad = std_mission_tid_gy * 0.1
    
    print(f"Final Mission TID: {mission_tid_gy:.2f} Gy ({mission_tid_krad:.2f} krad)")
    
    return mission_tid_krad, std_mission_tid_krad

# SIMULATION PARAMETERS
ELECTRON_FLUX = 3.2429E+08  
PROTON_FLUX = 5.1308E+07

SIMULATED_ELECTRONS = 20000000
SIMULATED_PROTONS = 100000000

MISSION_DAYS = 30 
TARGET_MASS_KG = 0.22834

# DATA FILES (Keys = Peak Magnetic Field in Tesla)
ELECTRON_FILES = {
    0.0: "GEANT4_data/build/T_sweep/cubic/E2_T_00_Al_05.csv",
    0.2: "GEANT4_data/build/T_sweep/cubic/E2_T_02_Al_05.csv",
    0.5: "GEANT4_data/build/T_sweep/cubic/E2_T_05_Al_05.csv",
    1.0: "GEANT4_data/build/T_sweep/cubic/E2_T_10_Al_05.csv",
}

PROTON_FILES = {
    0.0: "GEANT4_data/build/T_sweep/cubic/P2_T_00_Al_05.csv",
    0.2: "GEANT4_data/build/T_sweep/cubic/P2_T_02_Al_05.csv",
    0.5: "GEANT4_data/build/T_sweep/cubic/P2_T_05_Al_05.csv",
    1.0: "GEANT4_data/build/T_sweep/cubic/P2_T_10_Al_05.csv",
}

# EXECUTE CALCULATIONS & CONVERT X-AXIS
b_peak_values = sorted(list(ELECTRON_FILES.keys()))
tid_e = []
std_e = []
tid_p = []
std_p = []
x_values_dipole = []

# Vault boundary radius in meters
radius_m = 0.20 

for b_peak in b_peak_values:
    # Formula: B_peak = 10^-7 * (2m / r^3)  =>  m = (B_peak * r^3) / (2 * 10^-7)
    dipole_moment = (b_peak * (radius_m**3)) / (2 * 1e-7)
    
    # Scale to 10^5 for a cleaner X-axis on the plot
    x_values_dipole.append(dipole_moment / 1e5) 
    
    # Calculate Electrons
    t_e, s_e = calculate_mission_tid(
        file_path=ELECTRON_FILES[b_peak], 
        particle_type=f"Electrons (B={b_peak}T)",
        simulated_particles=SIMULATED_ELECTRONS,
        spenvis_flux=ELECTRON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    tid_e.append(t_e if t_e is not None else 0.0)
    std_e.append(s_e if s_e is not None else 0.0)

    # Calculate Protons
    t_p, s_p = calculate_mission_tid(
        file_path=PROTON_FILES[b_peak], 
        particle_type=f"Protons (B={b_peak}T)",
        simulated_particles=SIMULATED_PROTONS,
        spenvis_flux=PROTON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    tid_p.append(t_p if t_p is not None else 0.0)
    std_p.append(s_p if s_p is not None else 0.0)

# PLOTTING
if any(tid_e) or any(tid_p):
    print("\nGenerating TID Line Plot...")
    
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    c_elec = '#1f77b4' # Deep Blue
    c_prot = '#d62728' # Deep Red
    
    # Plot both lines with error bars (styled for scientific publication)
    ax.errorbar(x_values_dipole, tid_e, yerr=std_e, fmt="-s", color=c_elec, 
                ecolor="dimgray", elinewidth=1.2, 
                markersize=8, markerfacecolor="white", markeredgecolor=c_elec, markeredgewidth=1.5,
                linewidth=2.5, capsize=4, capthick=1.2, zorder=3, label='Electrons')
                
    ax.errorbar(x_values_dipole, tid_p, yerr=std_p, fmt="-o", color=c_prot, 
                ecolor="dimgray", elinewidth=1.2, 
                markersize=8, markerfacecolor="white", markeredgecolor=c_prot, markeredgewidth=1.5,
                linewidth=2.5, capsize=4, capthick=1.2, zorder=3, label='Protons')
    
    ax.set_title('Total Ionizing Dose vs. Magnetic Dipole Moment (5 mm Al Vault)', fontsize=14, pad=15)
    ax.set_xlabel(r'Magnetic Dipole Moment ($\times 10^5$ A$\cdot$m$^2$)', fontsize=13)
    ax.set_ylabel('Total Ionizing Dose (krad)', fontsize=13)
    
    ax.set_yscale('log') 
    
    # Add numerical labels atop points for both sets (shifted slightly higher to clear error bars)
    for x, y, err in zip(x_values_dipole, tid_e, std_e):
        if y > 0:
            ax.annotate(f"{y:,.1f}" if y > 0.1 else f"{y:.2e}", xy=(x, y + err), 
                        xytext=(5, 12), textcoords='offset points', 
                        ha='center', va='bottom', fontsize=10, color=c_elec)
                        
    for x, y, err in zip(x_values_dipole, tid_p, std_p):
        if y > 0:
            ax.annotate(f"{y:,.1f}" if y > 0.1 else f"{y:.2e}", xy=(x, y + err), 
                        xytext=(0, 12), textcoords='offset points', 
                        ha='center', va='bottom', fontsize=10, color=c_prot)
    
    # Adjust Y-limits dynamically based on both datasets
    all_valid_tids = [y for y in tid_e + tid_p if y > 0]
    if all_valid_tids:
        ax.set_ylim(bottom=min(all_valid_tids) * 0.4, top=max(all_valid_tids) * 5.0)
    
    ax.legend(fontsize=12, loc='upper right')
    
    ax.grid(axis='y', which='major', linestyle='-', alpha=0.4, color='gray', zorder=0)
    ax.grid(axis='y', which='minor', linestyle=':', alpha=0.2, color='gray', zorder=0)
    ax.grid(axis='x', which='major', linestyle='--', alpha=0.3, color='gray', zorder=0)
    
    fig.tight_layout()
    plt.show()
else:
    print("No valid data found to plot. Check your file paths.")