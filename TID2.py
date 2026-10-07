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


def calculate_mission_tid(
    file_path,
    particle_type,
    simulated_particles,
    spenvis_flux,
    mission_duration_days,
    target_mass_kg,
):
    """
    Calculate 30-day TID and its 1-sigma Monte Carlo statistical uncertainty
    using a history-by-history estimator.

    Required CSV columns:
        EventID, Ekin_MeV, Edep_MeV

    EventID must identify the primary GEANT4 history. Histories with no
    deposition do not need to be explicitly present in the CSV; they are
    included as zero-contribution histories through simulated_particles.
    """
    print(f"\n--- TID Calculation for {particle_type} ---")

    try:
        df = pd.read_csv(file_path, comment="#")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None

    required_columns = {"EventID", "Edep_MeV"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(
            f"{file_path} must contain the columns {sorted(required_columns)}. "
            f"Missing: {sorted(missing)}. "
            "The GEANT4 output must retain the primary EventID for a "
            "history-by-history uncertainty estimate."
        )

    df["EventID"] = pd.to_numeric(df["EventID"], errors="coerce")
    df["Edep_MeV"] = pd.to_numeric(df["Edep_MeV"], errors="coerce")
    df = df.dropna(subset=["EventID", "Edep_MeV"])

    if simulated_particles <= 1:
        raise ValueError("simulated_particles must be greater than 1.")

    # Sum all energy-deposition contributions belonging to each primary
    # history. A history can generate multiple hits through primary/secondary
    # interactions, so the history contribution is the sum of all Edep values.
    history_edep = df.groupby("EventID", sort=False)["Edep_MeV"].sum()

    deposited_energy_j = history_edep.to_numpy() * 1.602176634e-13

    # History-by-history estimator:
    # X_i = energy deposited in the sensitive volume by primary history i.
    #
    # Histories absent from the CSV are zero-deposition histories and are
    # therefore included implicitly in the population of N simulated histories.
    N = int(simulated_particles)
    sum_x = deposited_energy_j.sum()
    sum_x2 = np.square(deposited_energy_j).sum()

    mean_x = sum_x / N

    # Sample variance of the per-history scored quantity, including the
    # zero-deposition histories that are not explicitly stored in the CSV.
    variance_x = (sum_x2 - (sum_x ** 2) / N) / (N - 1)
    variance_x = max(variance_x, 0.0)

    standard_error_mean_x = np.sqrt(variance_x / N)

    simulated_dose_gy_per_history = mean_x / target_mass_kg
    uncertainty_simulated_dose_gy_per_history = (
        standard_error_mean_x / target_mass_kg
    )

    # Mission environment scaling
    sphere_radius_cm = 80.0
    sphere_area_cm2 = np.pi * (sphere_radius_cm ** 2)

    particles_per_second = spenvis_flux * sphere_area_cm2
    mission_seconds = mission_duration_days * 24 * 3600
    total_mission_particles = particles_per_second * mission_seconds

    mission_tid_gy = (
        simulated_dose_gy_per_history * total_mission_particles
    )
    uncertainty_mission_tid_gy = (
        uncertainty_simulated_dose_gy_per_history * total_mission_particles
    )

    mission_tid_krad = mission_tid_gy * 0.1
    uncertainty_mission_tid_krad = uncertainty_mission_tid_gy * 0.1

    relative_uncertainty = (
        uncertainty_mission_tid_krad / mission_tid_krad
        if mission_tid_krad > 0
        else np.nan
    )

    print(f"Simulated primary histories: {N:,}")
    print(f"Histories with recorded deposition: {len(history_edep):,}")
    print(f"Total Energy Deposited: {history_edep.sum():.2e} MeV")
    print(
        f"Final Mission TID: {mission_tid_krad:.3g} +/- "
        f"{uncertainty_mission_tid_krad:.3g} krad (1 sigma)"
    )
    if np.isfinite(relative_uncertainty):
        print(f"Relative MC uncertainty: {100.0 * relative_uncertainty:.3f}%")

    return mission_tid_krad, uncertainty_mission_tid_krad


# SIMULATION PARAMETERS
ELECTRON_FLUX = 3.2429E+08
PROTON_FLUX = 5.1308E+07

SIMULATED_ELECTRONS = 20000000
SIMULATED_PROTONS = 100000000

MISSION_DAYS = 30
TARGET_MASS_KG = 0.22834


# DATA FILES (keys = reference magnetic field in Tesla)
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
b_peak_values = sorted(ELECTRON_FILES.keys())

tid_e = []
std_e = []
tid_p = []
std_p = []
x_values_dipole = []

radius_m = 0.20

for b_peak in b_peak_values:
    # Equatorial dipole field relation used for the figure axis:
    # B_ref = 2e-7 * m / r^3  ->  m = B_ref * r^3 / (2e-7)
    dipole_moment = (b_peak * (radius_m ** 3)) / (2 * 1e-7)
    x_values_dipole.append(dipole_moment / 1e5)

    t_e, s_e = calculate_mission_tid(
        file_path=ELECTRON_FILES[b_peak],
        particle_type=f"Electrons (B={b_peak}T)",
        simulated_particles=SIMULATED_ELECTRONS,
        spenvis_flux=ELECTRON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG,
    )
    tid_e.append(t_e if t_e is not None else 0.0)
    std_e.append(s_e if s_e is not None else 0.0)

    t_p, s_p = calculate_mission_tid(
        file_path=PROTON_FILES[b_peak],
        particle_type=f"Protons (B={b_peak}T)",
        simulated_particles=SIMULATED_PROTONS,
        spenvis_flux=PROTON_FLUX,
        mission_duration_days=MISSION_DAYS,
        target_mass_kg=TARGET_MASS_KG,
    )
    tid_p.append(t_p if t_p is not None else 0.0)
    std_p.append(s_p if s_p is not None else 0.0)


# PLOTTING
fig, ax = plt.subplots(figsize=(10, 6.5))

c_elec = '#1f77b4'
c_prot = '#d62728'

ax.errorbar(
    x_values_dipole,
    tid_e,
    yerr=std_e,
    fmt="-s",
    color=c_elec,
    ecolor="dimgray",
    elinewidth=1.2,
    markersize=8,
    markerfacecolor="white",
    markeredgecolor=c_elec,
    markeredgewidth=1.5,
    linewidth=2.0,
    capsize=4,
    capthick=1.2,
    zorder=3,
    label="Electrons",
)

ax.errorbar(
    x_values_dipole,
    tid_p,
    yerr=std_p,
    fmt="-o",
    color=c_prot,
    ecolor="dimgray",
    elinewidth=1.2,
    markersize=8,
    markerfacecolor="white",
    markeredgecolor=c_prot,
    markeredgewidth=1.5,
    linewidth=2.0,
    capsize=4,
    capthick=1.2,
    zorder=3,
    label="Protons",
)

ax.set_title(
    "Total Ionizing Dose vs. Magnetic Dipole Moment (5 mm Al Vault)",
    fontsize=14,
    pad=15,
)
ax.set_xlabel(
    r"Magnetic Dipole Moment ($\times 10^5$ A$\cdot$m$^2$)",
    fontsize=13,
)
ax.set_ylabel("Total Ionizing Dose (krad)", fontsize=13)
ax.set_yscale("log")

ax.legend(fontsize=12, loc="upper right")
ax.grid(axis="y", which="major", linestyle="-", alpha=0.4, color="gray", zorder=0)
ax.grid(axis="y", which="minor", linestyle=":", alpha=0.2, color="gray", zorder=0)
ax.grid(axis="x", which="major", linestyle="--", alpha=0.3, color="gray", zorder=0)

fig.tight_layout()
plt.show()
