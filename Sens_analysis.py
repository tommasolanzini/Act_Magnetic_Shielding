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
    "legend.frameon": False,
    "axes.grid": False
})

def plot_hit_sensitivity(file_path, total_simulated_particles, spenvis_flux,
                         mission_duration_days, target_mass_kg, steps=10):
        
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

    total_hits = len(df)
    if total_hits == 0:
        print("Error: No valid hits found in file.")
        return
        
    print(f"Total hits: {total_hits}")

    sphere_radius_cm = 80.0
    sphere_area_cm2 = np.pi * sphere_radius_cm**2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = spenvis_flux * sphere_area_cm2 * mission_seconds

    fractions = [1/1000, 1/500, 1/200, 1/100, 1/50, 1/20, 1/10, 1/5, 1/2, 1.0]
    
    n_hits_list = []
    tid_list = []

    for f in fractions:
        n_hits = int(total_hits * f)
        if n_hits == 0:
            continue
            
        subset = df.sample(n=n_hits)
        
        sim_particles_frac = total_simulated_particles * f
        
        energy_joules = subset[edep_col].sum() * 1.602176634e-13
        simulated_dose_gy = energy_joules / target_mass_kg
        scaling_factor = total_mission_particles / sim_particles_frac
        
        mission_tid_gy = simulated_dose_gy * scaling_factor
        mission_tid_krad = mission_tid_gy * 0.1
        
        n_hits_list.append(n_hits)
        tid_list.append(mission_tid_krad)
        
        print(f"Fraction: {f*100:6.2f}% | Evaluated Hits: {n_hits:8d} | "
              f"Sim. Particles: {sim_particles_frac:.2e} | TID: {mission_tid_krad:.4f} krad")

    fig, ax = plt.subplots(figsize=(7, 5))
    
    ax.plot(n_hits_list, tid_list, marker="o", color="teal", 
            linewidth=2, markersize=7, markeredgecolor="darkslategray",
            markerfacecolor="mediumturquoise", zorder=3)
    
    final_tid = tid_list[-1]
    
    # Calculate and plot the +- 5% tolerance band
    upper_bound = final_tid * 1.05
    lower_bound = final_tid * 0.95
    
    ax.axhspan(lower_bound, upper_bound, color="gray", alpha=0.15, 
               label=r"$\pm 5\%$ Tolerance", zorder=1)
               
    ax.axhline(final_tid, color="gray", linestyle="--", alpha=0.6, 
               label=f"Asymptotic value ({final_tid:.3f} krad)", zorder=2)

    ax.set_title("TID Convergence vs. Number of Evaluated Hits", fontsize=12, pad=12)
    ax.set_xlabel("Evaluated Energy-deposition Hits", fontsize=11)
    ax.set_ylabel("Total Ionizing Dose (krad)", fontsize=11)
    ax.legend(loc="best")
    
    ax.grid(axis="both", which="major", linestyle="--", color="gray", alpha=0.2, zorder=0)
    ax.set_ybound(lower=0)
    
    y_max = max(max(tid_list) * 1.1, upper_bound * 1.1)
    ax.set_ybound(upper=y_max)
    
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    FILE_PATH = "build/T_sweep/Brem_search/E2_T_20_Al_05_SC.csv"
    TOTAL_SIMULATED_PROTONS = 2000000000
    PROTON_FLUX = 1.4667E+11
    MISSION_DAYS = 30
    TARGET_MASS_KG = 0.22834
    
    plot_hit_sensitivity(
        file_path=FILE_PATH,
        total_simulated_particles=TOTAL_SIMULATED_PROTONS,
        spenvis_flux=PROTON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG,
        steps=10  
    )