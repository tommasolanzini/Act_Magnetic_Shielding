import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_mission_tid(file_path, particle_type, simulated_particles, spenvis_flux, mission_duration_days, target_mass_kg):
    print(f"\n--- TID Calculation for {particle_type.upper()} ---")
    
    try:
        df = pd.read_csv(file_path, comment='#', names=['Edep_MeV'])
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None
        
    # NEW LINE: Force the column to be numeric, turning any text into NaN, then drop the NaNs
    df['Edep_MeV'] = pd.to_numeric(df['Edep_MeV'], errors='coerce').dropna()
    
    total_energy_mev = df['Edep_MeV'].sum()
    
    print(f"Simulated Hits: {len(df)}")
    print(f"Total Energy Deposited: {total_energy_mev:.2e} MeV")
    # 1. Convert to Joules (1 MeV = 1.602e-13 Joules)
    total_energy_joules = total_energy_mev * 1.602e-13
    
    # 2. Calculate Raw Simulation Dose (Grays)
    simulated_dose_gy = total_energy_joules / target_mass_kg
    
    # 3. Mission Environment Scaling
    sphere_radius_cm = 15.0
    sphere_area_cm2 = 4 * np.pi * (sphere_radius_cm ** 2)
    
    particles_per_second = spenvis_flux * sphere_area_cm2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = particles_per_second * mission_seconds
    
    # Scale the dose
    scaling_factor = total_mission_particles / simulated_particles
    mission_tid_gy = simulated_dose_gy * scaling_factor
    mission_tid_krad = mission_tid_gy * 0.1 # 1 Gy = 100 rad = 0.1 krad
    
    print("\n--- RESULTS ---")
    print(f"Target Mass: {target_mass_kg:.3f} kg")
    print(f"Simulation Dose: {simulated_dose_gy:.2e} Gy")
    print(f"Scaling Factor (Mission/Simulated): {scaling_factor:.2e}")
    print(f"Final Mission TID: {mission_tid_gy:.2f} Gy ({mission_tid_krad:.2f} krad)")
    
    return mission_tid_krad, df['Edep_MeV']


# SIMULATION PARAMETERS

ELECTRON_FLUX = 1.2569E+10
PROTON_FLUX = 1.4667E11
SIMULATED_PARTICLES = 1E6
MISSION_DAYS = 30 
# TARGET_MASS_KG = 0.000466
TARGET_MASS_KG = 0.22834


# EXECUTE CALCULATIONS

# Point these directly to your merged files
elec_tid, elec_edep = calculate_mission_tid(
    file_path="GEANT4_data/build/electrons_2_data.csv", 
    particle_type="Electrons",
    simulated_particles=SIMULATED_PARTICLES,
    spenvis_flux=ELECTRON_FLUX,
    mission_duration_days=MISSION_DAYS,
    target_mass_kg=TARGET_MASS_KG
)

prot_tid, prot_edep = calculate_mission_tid(
    file_path="GEANT4_data/build/protons_2_data.csv", 
    particle_type="Protons",
    simulated_particles=SIMULATED_PARTICLES,
    spenvis_flux=PROTON_FLUX,
    mission_duration_days=MISSION_DAYS,
    target_mass_kg=TARGET_MASS_KG
)


# PLOTTING

if elec_tid is not None and prot_tid is not None:
    print("\nGenerating plots...")
    
    # Plot 1: Total Dose Comparison (Bar Chart)
    plt.figure(figsize=(9, 6.5))
    bars = plt.bar(['Electrons', 'Protons'], [elec_tid, prot_tid], color=['#1f77b4', '#d62728'], edgecolor='black')
    
    plt.title('30-Day Jovian Mission TID: Electrons vs. Protons', fontsize=16, fontweight='bold', pad=15)
    plt.ylabel('Total Ionizing Dose (krad)', fontsize=14, fontweight='bold')
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    
    # Logarithmic scale to handle the massive difference
    plt.yscale('log')
    
    # Enhanced grid for log scale
    plt.grid(axis='y', which='major', linestyle='-', alpha=0.6)
    plt.grid(axis='y', which='minor', linestyle='--', alpha=0.3)
    
    # Add numerical labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        # Multiply by 1.3 to push the text up appropriately on a log scale
        plt.text(bar.get_x() + bar.get_width()/2, yval * 1.3, 
                 f"{yval:,.1f} krad", ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Adjust y-limits to give the text room to breathe at the top
    plt.ylim(bottom=10, top=max(elec_tid, prot_tid) * 10)
    
    plt.tight_layout()
    plt.show()

    # Plot 2: Energy Deposition Histogram
    plt.figure(figsize=(10, 6))
    # Filter out zero-energy hits for cleaner log plotting
    e_clean = elec_edep[elec_edep > 0]
    p_clean = prot_edep[prot_edep > 0]
    
    plt.hist(e_clean, bins=np.logspace(np.log10(e_clean.min()), np.log10(e_clean.max()), 50), 
             alpha=0.6, label='Electrons', color='#1f77b4', density=True)
    plt.hist(p_clean, bins=np.logspace(np.log10(p_clean.min()), np.log10(p_clean.max()), 50), 
             alpha=0.6, label='Protons', color='#d62728', density=True)
    
    plt.title('Energy Deposition Spectrum per Hit (Passive Baseline)', fontsize=14)
    plt.xlabel('Deposited Energy (MeV)', fontsize=12)
    plt.ylabel('Normalized Frequency', fontsize=12)
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.4)
    plt.show()