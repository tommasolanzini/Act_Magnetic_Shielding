import pandas as pd
import matplotlib.pyplot as plt

# CSV files
orbit1_protons = "spenvis_tr_protons.csv"
orbit2_protons = "spenvis_tr_protons_2.csv"
orbit1_electrons = "spenvis_tr_electrons.csv"
orbit2_electrons = "spenvis_tr_electrons_2.csv"

# Load data
p1 = pd.read_csv(orbit1_protons)
p2 = pd.read_csv(orbit2_protons)
e1 = pd.read_csv(orbit1_electrons)
e2 = pd.read_csv(orbit2_electrons)

# Proton flux
plt.figure(figsize=(10, 7))
plt.loglog(p1["Energy"], p1["Flux"], label="Orbit 1")
plt.loglog(p2["Energy"], p2["Flux"], label="Orbit 2")
plt.xlabel("Energy (MeV)")
plt.ylabel("Proton Flux")
plt.title("Proton Flux")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

# Electron flux
plt.figure(figsize=(10, 7))
plt.loglog(e1["Energy"], e1["Flux"], label="Orbit 1")
plt.loglog(e2["Energy"], e2["Flux"], label="Orbit 2")
plt.xlabel("Energy (MeV)")
plt.ylabel("Electron Flux")
plt.title("Electron Flux")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

plt.show()
