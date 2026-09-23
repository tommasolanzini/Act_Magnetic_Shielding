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
    print(f"\n--- TID Calculation for {particle_type.upper()} ---")
    
    try:
        df = pd.read_csv(file_path, comment='#', names=['Ekin_MeV', 'Edep_MeV'])
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None
        
    df['Ekin_MeV'] = pd.to_numeric(df['Ekin_MeV'], errors='coerce')
    df['Edep_MeV'] = pd.to_numeric(df['Edep_MeV'], errors='coerce')
    df = df.dropna()
    
    total_energy_mev = df['Edep_MeV'].sum()
    
    print(f"Simulated Hits: {len(df)}")
    print(f"Total Energy Deposited: {total_energy_mev:.2e} MeV")
    
    # Convert to Joules and calculate dose
    total_energy_joules = total_energy_mev * 1.602176634e-13
    simulated_dose_gy = total_energy_joules / target_mass_kg
    
    # 3. Mission Environment Scaling (80 cm spawning sphere)
    sphere_radius_cm = 80.0 
    sphere_area_cm2 = np.pi * (sphere_radius_cm ** 2) # CORRECT
    
    particles_per_second = spenvis_flux * sphere_area_cm2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = particles_per_second * mission_seconds
    
    scaling_factor = total_mission_particles / simulated_particles
    mission_tid_gy = simulated_dose_gy * scaling_factor
    mission_tid_krad = mission_tid_gy * 0.1 
    
    print(f"Final Mission TID: {mission_tid_gy:.2f} Gy ({mission_tid_krad:.2f} krad)")
    
    return mission_tid_krad, df['Edep_MeV']



# SIMULATION PARAMETERS

# PROTON_FLUX = 8.9174E+07	
# ELECTRON_FLUX = 5.9311E+08

ELECTRON_FLUX = 1.2569E+10  
PROTON_FLUX = 1.4667E+11

SIMULATED_PROTONS = 20000000
SIMULATED_ELECTRONS = 20000000

MISSION_DAYS = 30 
TARGET_MASS_KG = 0.22834

PROTON_FILES = {
    "0 mm Al": "GEANT4_data/build/T_sweep/pay2/P2_T_0_Al_0.csv",
    "1 mm Al": "GEANT4_data/build/T_sweep/pay2/P2_T_0_Al_01.csv",
    "2 mm Al": "GEANT4_data/build/T_sweep/pay2/P2_T_0_Al_02.csv",
    "3 mm Al": "GEANT4_data/build/T_sweep/pay2/P2_T_0_Al_03.csv",
    "5 mm Al": "GEANT4_data/build/T_sweep/pay2/P2_T_0_Al_05.csv"

}

ELECTRON_FILES = {
    "0 mm Al": "GEANT4_data/build/T_sweep/pay2/E2_T_0_Al_0.csv",
    "1 mm Al": "GEANT4_data/build/T_sweep/pay2/E2_T_0_Al_01.csv",
    "2 mm Al": "GEANT4_data/build/T_sweep/pay2/E2_T_0_Al_02.csv",
    "3 mm Al": "GEANT4_data/build/T_sweep/pay2/E2_T_0_Al_03.csv",
    "5 mm Al": "GEANT4_data/build/T_sweep/pay2/E2_T_0_Al_05.csv"

}


# EXECUTE CALCULATIONS
labels = list(PROTON_FILES.keys())
tid_p = []
tid_e = []

# Calculate Protons
for label, file_path in PROTON_FILES.items():
    tid, _ = calculate_mission_tid(
        file_path=file_path, 
        particle_type=f"Protons ({label.replace(chr(10), ' ')})",
        simulated_particles=SIMULATED_PROTONS,
        spenvis_flux=PROTON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    tid_p.append(tid if tid is not None else 0.0)

# Calculate Electrons
for label, file_path in ELECTRON_FILES.items():
    tid, _ = calculate_mission_tid(
        file_path=file_path, 
        particle_type=f"Electrons ({label.replace(chr(10), ' ')})",
        simulated_particles=SIMULATED_ELECTRONS,
        spenvis_flux=ELECTRON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    tid_e.append(tid if tid is not None else 0.0)


# PLOTTING

if any(tid_p) or any(tid_e):
    print("\nGenerating TID Comparison Plot...")
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    x = np.arange(len(labels))
    width = 0.35 
    
    c_prot = '#d62728' # Deep Red
    c_elec = '#1f77b4' # Deep Blue
    
    # Plot side-by-side grouped bars
    bars_p = ax.bar(x - width/2, tid_p, width, color=c_prot, edgecolor='black', linewidth=1.5, label='Protons')
    bars_e = ax.bar(x + width/2, tid_e, width, color=c_elec, edgecolor='black', linewidth=1.5, label='Electrons')
    
    ax.set_title('30-Day Jovian Mission Total Dose: Protons vs. Electrons', fontsize=14, pad=15)
    ax.set_ylabel('Total Ionizing Dose (krad)', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    
    # Log scale is necessary to visualize both particles simultaneously
    ax.set_yscale('log') 
    
    # Add numerical labels atop bars
    for bars in [bars_p, bars_e]:
        for bar in bars:
            yval = bar.get_height()
            if yval > 0: # Only label if there is an actual dose
                text_label = f"{yval:,.1f}" if yval > 0.1 else f"{yval:.1e}"
                ax.text(bar.get_x() + bar.get_width()/2, yval * 1.25, 
                         text_label, ha='center', va='bottom', fontsize=10, rotation=0)
    
    # Add headroom to the top of the y-axis so labels don't clip
    max_val = max(max(tid_p), max(tid_e))
    # Bottom limit set to 1e-3 to prevent log-scale crashes if a dose is exactly 0
    ax.set_ylim(bottom=1e2, top=max_val * 5) 
    
    ax.legend(fontsize=12, loc='upper right')
    
    # Enhanced grid for logarithmic scale readability
    ax.grid(axis='y', which='major', linestyle='-', alpha=0.4, color='gray')
    ax.grid(axis='y', which='minor', linestyle=':', alpha=0.2, color='gray')
    
    fig.tight_layout()
    fig.savefig('Total_TID_vs_Al_Thickness.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()
else:
    print("No valid data found to plot. Check your file paths.")