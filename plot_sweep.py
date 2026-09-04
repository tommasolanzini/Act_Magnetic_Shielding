import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_mission_tid(file_path, simulated_particles, spenvis_flux, mission_duration_days, target_mass_kg):
    try:
        df = pd.read_csv(file_path, comment='#', names=['Edep_MeV'])
    except FileNotFoundError:
        return None
        
    df['Edep_MeV'] = pd.to_numeric(df['Edep_MeV'], errors='coerce').dropna()
    total_energy_mev = df['Edep_MeV'].sum()
    
    # 1. Convert to Joules (1 MeV = 1.602e-13 Joules)
    total_energy_joules = total_energy_mev * 1.602e-13
    
    # 2. Calculate Raw Simulation Dose (Grays)
    simulated_dose_gy = total_energy_joules / target_mass_kg
    
    # 3. Mission Environment Scaling (80 cm sphere)
    sphere_radius_cm = 80.0 
    sphere_area_cm2 = 4 * np.pi * (sphere_radius_cm ** 2)
    
    particles_per_second = spenvis_flux * sphere_area_cm2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = particles_per_second * mission_seconds
    
    # 4. Scale the dose
    scaling_factor = total_mission_particles / simulated_particles
    mission_tid_gy = simulated_dose_gy * scaling_factor
    mission_tid_krad = mission_tid_gy * 0.1
    
    return mission_tid_krad

# --- SIMULATION PARAMETERS ---
PROTON_FLUX = 1.4667E11
ELECTRON_FLUX = 1.2569E+10

# Note: Ensure these match the exact beamOn numbers used in your Geant4 macros!
SIMULATED_PROTONS = 1E7
SIMULATED_ELECTRONS = 1E7 

MISSION_DAYS = 30 
# IMPORTANT: Verify this mass reflects your current Aluminum vault thickness
TARGET_MASS_KG = 0.22834 

tesla_values = ["0", "01", "02", "03", "05", "07", "1"]
prot_results = []
elec_results = []
total_results = []
valid_tesla = []

print("--- ANALYZING SWEEP DATA ---")

# --- PROCESS FILES ---
for b in tesla_values:
    file_prot = f"GEANT4_data/build/T_sweep/Al_02/Protons_T_{b}.csv"
    file_elec = f"GEANT4_data/build/T_sweep/Al_02/Electrons_T_{b}.csv"
    
    tid_prot = calculate_mission_tid(
        file_path=file_prot,
        simulated_particles=SIMULATED_PROTONS,
        spenvis_flux=PROTON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    
    tid_elec = calculate_mission_tid(
        file_path=file_elec,
        simulated_particles=SIMULATED_ELECTRONS,
        spenvis_flux=ELECTRON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG
    )
    
    if tid_prot is not None and tid_elec is not None:
        print(f"Magnetic Field: {b} T  -->  Protons: {tid_prot:,.2f} krad | Electrons: {tid_elec:,.2f} krad")
        prot_results.append(tid_prot)
        elec_results.append(tid_elec)
        total_results.append(tid_prot + tid_elec)
        valid_tesla.append(b)
    else:
        print(f"Warning: Missing data for {b} T. Ensure BOTH {file_prot} and {file_elec} exist.")

# --- PLOTTING ---
if valid_tesla:
    plt.figure(figsize=(10, 6.5))
    
    # Plot the individual curves
    plt.plot(valid_tesla, prot_results, marker='o', linestyle='-', color='#d62728', 
             linewidth=2, markersize=7, label='Proton Dose')
             
    plt.plot(valid_tesla, elec_results, marker='s', linestyle='-', color='#1f77b4', 
             linewidth=2, markersize=7, label='Electron Dose')
             
    # Plot the combined total dose curve
    plt.plot(valid_tesla, total_results, marker='^', linestyle='--', color='black', 
             linewidth=2.5, markersize=8, label='Total Accumulated Dose')
    
    # Academic formatting
    plt.title('Shielding Performance: TID vs. Magnetic Field Strength', fontsize=15, fontweight='bold', pad=15)
    plt.xlabel('Magnetic Field Strength at Vault Boundary (Tesla)', fontsize=13)
    plt.ylabel('Total Ionizing Dose (krad)', fontsize=13)
    
    plt.xticks(valid_tesla, fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    
    # Annotate the total dose data points with their values
    for x, t in zip(valid_tesla, total_results):
        plt.text(x, t + (max(total_results)*0.03), f'{t:,.0f}', 
                 ha='center', va='bottom', fontsize=11, fontweight='bold')
                 
    plt.ylim(bottom=0, top=max(total_results) * 1.15)
    
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
else:
    print("No valid CSV file pairs were found to plot.")