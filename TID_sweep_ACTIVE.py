import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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


def calculate_mission_tid(file_path, simulated_particles, spenvis_flux,
                          mission_duration_days, target_mass_kg):
    try:
        df = pd.read_csv(file_path, comment="#", names=["Ekin_MeV", "Edep_MeV"])
    except FileNotFoundError:
        print(f"Error: '{file_path}' was not found.")
        return None, None

    df["Ekin_MeV"] = pd.to_numeric(df["Ekin_MeV"], errors="coerce")
    df["Edep_MeV"] = pd.to_numeric(df["Edep_MeV"], errors="coerce")
    df = df.dropna()

    # Calculate total energy and its standard deviation (MC error: sqrt(sum of squares))
    edep_joules = df["Edep_MeV"] * 1.602176634e-13
    total_energy_joules = edep_joules.sum()
    std_energy_joules = np.sqrt((edep_joules**2).sum())

    simulated_dose_gy = total_energy_joules / target_mass_kg
    std_simulated_dose_gy = std_energy_joules / target_mass_kg

    sphere_radius_cm = 80.0
    sphere_area_cm2 = np.pi * sphere_radius_cm**2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = spenvis_flux * sphere_area_cm2 * mission_seconds

    scaling_factor = total_mission_particles / simulated_particles
    
    mission_tid_gy = simulated_dose_gy * scaling_factor
    std_mission_tid_gy = std_simulated_dose_gy * scaling_factor

    # Return TID and its Standard Deviation in krad
    return mission_tid_gy * 0.1, std_mission_tid_gy * 0.1


ELECTRON_FLUX = 3.2429E+08
PROTON_FLUX = 1.4667E+11
SIMULATED_ELECTRONS = 20000000  
SIMULATED_PROTONS = 100000000
MISSION_DAYS = 30
TARGET_MASS_KG = 0.22834

# Orbit 1: proton environment
ORBIT1_PROTON_FILES = {
    0.0: "GEANT4_data/build/T_sweep/stormer_pay/P1_T_00_Al_05.csv",
    # 0.1: "GEANT4_data/build/T_sweep/cubic/P1_T_01_Al_05.csv",
    0.2: "GEANT4_data/build/T_sweep/stormer_pay/P1_T_02_Al_05.csv",
    # 0.3: "GEANT4_data/build/T_sweep/cubic/P1_T_03_Al_05.csv",
    0.5: "GEANT4_data/build/T_sweep/stormer_pay/P1_T_05_Al_05.csv",
    1.0: "GEANT4_data/build/T_sweep/stormer_pay/P1_T_10_Al_05.csv",
    2.0: "GEANT4_data/build/T_sweep/stormer_pay/P1_T_20_Al_05.csv",
}

# Orbit 2: electron environment
ORBIT2_ELECTRON_FILES = {
    0.0: "GEANT4_data/build/T_sweep/stormer_pay/E2_T_00_Al_05.csv",
    0.2: "GEANT4_data/build/T_sweep/stormer_pay/E2_T_02_Al_05.csv",
    0.5: "GEANT4_data/build/T_sweep/stormer_pay/E2_T_05_Al_05.csv",
    1.0: "GEANT4_data/build/T_sweep/stormer_pay/E2_T_10_Al_05.csv",
    2.0: "GEANT4_data/build/T_sweep/stormer_pay/E2_T_20_Al_05.csv",
}

radius_m = 0.20

def dipole_moment(b_peak):
    return (b_peak * radius_m**3) / (2 * 1e-7) / 1e5

b_values_1 = sorted(ORBIT1_PROTON_FILES)
b_values_2 = sorted(ORBIT2_ELECTRON_FILES)

x_1 = [dipole_moment(b) for b in b_values_1]
x_2 = [dipole_moment(b) for b in b_values_2]

# Unpack the tuples returned by the updated function
results_1 = [calculate_mission_tid(
    ORBIT1_PROTON_FILES[b], SIMULATED_PROTONS, PROTON_FLUX,
    MISSION_DAYS, TARGET_MASS_KG
) for b in b_values_1]
tid_1 = [res[0] for res in results_1]
std_1 = [res[1] for res in results_1]

results_2 = [calculate_mission_tid(
    ORBIT2_ELECTRON_FILES[b], SIMULATED_ELECTRONS, ELECTRON_FLUX,
    MISSION_DAYS, TARGET_MASS_KG
) for b in b_values_2]
tid_2 = [res[0] for res in results_2]
std_2 = [res[1] for res in results_2]

# --- Plot 1 ---
fig1, ax1 = plt.subplots(figsize=(6, 4.8))

# Styled for scientific publication
ax1.errorbar(x_1, tid_1, yerr=std_1, fmt="-o", color="firebrick", 
             ecolor="dimgray", elinewidth=1.2, 
             markersize=6, markerfacecolor="white", markeredgecolor="firebrick", markeredgewidth=1.5,
             linewidth=1.8, capsize=3.5, capthick=1.2, zorder=3)

ax1.set_title("Orbit 1 - Protons", fontsize=12, pad=10)
ax1.set_xlabel(r"Magnetic Dipole Moment ($\times 10^5$ A$\cdot$m$^2$)")
ax1.set_ylabel("Total Ionizing Dose (krad)")
ax1.set_yscale("log")

# Cleaner grid styling
ax1.grid(axis="y", which="major", linestyle="-", color="gray", alpha=0.2, zorder=0)
ax1.grid(axis="y", which="minor", linestyle=":", color="gray", alpha=0.1, zorder=0)
ax1.grid(axis="x", which="major", linestyle="--", color="gray", alpha=0.15, zorder=0)

fig1.tight_layout()
plt.show()


# --- Plot 2 ---
fig2, ax2 = plt.subplots(figsize=(6, 4.8))

# Styled for scientific publication
ax2.errorbar(x_2, tid_2, yerr=std_2, fmt="-s", color="forestgreen", 
             ecolor="dimgray", elinewidth=1.2, 
             markersize=6, markerfacecolor="white", markeredgecolor="forestgreen", markeredgewidth=1.5,
             linewidth=1.8, capsize=3.5, capthick=1.2, zorder=3)

ax2.set_title("Orbit 2 - Electrons", fontsize=12, pad=10)
ax2.set_xlabel(r"Magnetic Dipole Moment ($\times 10^5$ A$\cdot$m$^2$)")
ax2.set_ylabel("Total Ionizing Dose (krad)")
ax2.set_yscale("log")

# Cleaner grid styling
ax2.grid(axis="y", which="major", linestyle="-", color="gray", alpha=0.2, zorder=0)
ax2.grid(axis="y", which="minor", linestyle=":", color="gray", alpha=0.1, zorder=0)
ax2.grid(axis="x", which="major", linestyle="--", color="gray", alpha=0.15, zorder=0)

fig2.tight_layout()
plt.show()