import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df_spenvis = pd.read_csv('SPENVIS_data/spenvis_tr_protons.csv')
df_baseline = pd.read_csv('GEANT4_data/build/T_sweep/pay2/P_T_0_noshield.csv')
df_passivo = pd.read_csv('GEANT4_data/build/T_sweep/pay2/P_T_0.csv')
df_attivo_1 = pd.read_csv('GEANT4_data/build/T_sweep/pay2/P_T_2_noshield_40.csv')
df_attivo_2 = pd.read_csv('GEANT4_data/build/T_sweep/pay2/P_T_2_40.csv')
# df_passivo = pd.read_csv('GEANT4_data/build/T_sweep/Al_01/P_T_0_pads.csv')
# df_attivo_1 = pd.read_csv('GEANT4_data/build/T_sweep/Al_01/P_T_1_pads.csv')
# df_attivo_2 = pd.read_csv('GEANT4_data/build/T_sweep/Al_01/P_T_2_pads.csv')

energie_iniziali = df_spenvis['Energy'].values
flusso_iniziale = df_spenvis['Flux'].values

ekin_baseline = df_baseline['Ekin_MeV'].values
edep_baseline = df_baseline['Edep_MeV'].values

ekin_passive = df_passivo['Ekin_MeV'].values
edep_passive = df_passivo['Edep_MeV'].values

ekin_active_1 = df_attivo_1['Ekin_MeV'].values
edep_active_1 = df_attivo_1['Edep_MeV'].values
ekin_active_2 = df_attivo_2['Ekin_MeV'].values
edep_active_2 = df_attivo_2['Edep_MeV'].values

# Numero di primari
N_primari = 10000000 
pesi_baseline = np.ones_like(ekin_baseline) / N_primari
pesi_passivi = np.ones_like(ekin_passive) / N_primari
pesi_attivi_1 = np.ones_like(ekin_active_1) / (N_primari * 4) 
pesi_attivi_2 = np.ones_like(ekin_active_2) / (N_primari * 4)


# 2. CONVERSIONE SPENVIS IN FREQUENZA ASSOLUTA

# Creiamo i bin standard
E_min = 1e-3
E_max = 1e3
num_bins = 60
bins_log = np.logspace(np.log10(E_min), np.log10(E_max), num_bins)
bin_centers = (bins_log[:-1] + bins_log[1:]) / 2
bin_widths = np.diff(bins_log)

# Interpolazione logaritmica del flusso SPENVIS sui centri dei bin
log_E = np.log10(energie_iniziali)
log_F = np.log10(flusso_iniziale)
log_F_interp = np.interp(np.log10(bin_centers), log_E, log_F)
F_interp = 10**log_F_interp

F_interp[bin_centers < energie_iniziali[0]] = 0
F_interp[bin_centers > energie_iniziali[-1]] = 0

flusso_totale = np.trapz(flusso_iniziale, energie_iniziali)
prob_spenvis = (F_interp / flusso_totale) * bin_widths

# plots

# plt.plot(bin_centers, prob_spenvis, color='black', linewidth=2, 
#          linestyle=':', marker='o', markersize=4, label='Sorgente (SPENVIS)')
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

c_base = '#262626' # Dark Grey/Black for baseline
c_pass = '#C42021' # Deep Red
c_act1 = '#005BBB' # Deep Blue
c_act2 = '#228B22' # Forest Green

line_w = 2.0 
m_size = 5   # Marker size

# Helper function to extract line data from histogram bins
def get_line_data(data, bins, weights):
    counts, bin_edges = np.histogram(data, bins=bins, weights=weights)
    # Use geometric mean for bin centers on a logarithmic axis
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    
    # Filter out zero-count bins so the lines don't violently drop to zero 
    mask = counts > 0
    return bin_centers[mask], counts[mask]

# ==========================================
# 2. GRAFICO 1: ENERGIA CINETICA INCIDENTE
# ==========================================
fig1, ax1 = plt.subplots(figsize=(8, 5))

# Calculate data points
x_base, y_base = get_line_data(ekin_baseline, bins_log, pesi_baseline)
x_pass, y_pass = get_line_data(ekin_passive, bins_log, pesi_passivi)
x_act1, y_act1 = get_line_data(ekin_active_1, bins_log, pesi_attivi_1)
x_act2, y_act2 = get_line_data(ekin_active_2, bins_log, pesi_attivi_2)

# Plot with lines and distinct markers
ax1.plot(x_base, y_base, marker='o', markersize=m_size, linestyle='-', linewidth=line_w, color=c_base, label='Baseline')
ax1.plot(x_pass, y_pass, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive')
ax1.plot(x_act1, y_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label='Active (2 T) no Al')
ax1.plot(x_act2, y_act2, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label='Active (2 T)')

ax1.set_xlabel('Kinetic Energy (MeV)', fontsize=12)
ax1.set_ylabel(f'Absolute Frequency (Fraction of $10^{{{int(np.log10(N_primari))}}}$ primaries)', fontsize=12)

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim(bottom=(0.5 / N_primari)) 

ax1.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax1.legend(fontsize=11, loc='upper right')

fig1.tight_layout()
fig1.savefig('grafico_1_Ekin.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.show()

# ==========================================
# 3. GRAFICO 2: ENERGIA DEPOSITATA (Edep)
# ==========================================
fig2, ax2 = plt.subplots(figsize=(8, 5))

# Calculate data points (assuming edep variables exist in your environment)
# x_edep_base, y_edep_base = get_line_data(edep_baseline, bins_log, pesi_baseline)
x_edep_pass, y_edep_pass = get_line_data(edep_passive, bins_log, pesi_passivi)
x_edep_act1, y_edep_act1 = get_line_data(edep_active_1, bins_log, pesi_attivi_1)
x_edep_act2, y_edep_act2 = get_line_data(edep_active_2, bins_log, pesi_attivi_2)

# Plot with lines and distinct markers
# ax2.plot(x_edep_base, y_edep_base, marker='o', markersize=m_size, linestyle='-', linewidth=line_w, color=c_base, label='Baseline - Edep')
ax2.plot(x_edep_pass, y_edep_pass, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive')
ax2.plot(x_edep_act1, y_edep_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label='Active (2 T) no Al')
ax2.plot(x_edep_act2, y_edep_act2, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label='Active (2 T)')

ax2.set_xlabel('Deposited Energy (MeV)', fontsize=12)
ax2.set_ylabel(f'Absolute Frequency (Fraction of $10^{{{int(np.log10(N_primari))}}}$ primaries)', fontsize=12)

ax2.set_xscale('log')
# ax2.set_yscale('log') # Strongly recommended to keep this ON for Edep
ax2.set_ylim(bottom=(0.5 / N_primari))

ax2.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax2.legend(fontsize=11, loc='upper right')

fig2.tight_layout()
fig2.savefig('grafico_2_Edep.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.show()