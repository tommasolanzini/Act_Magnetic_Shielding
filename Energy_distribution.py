import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df_spenvis = pd.read_csv('SPENVIS_data/spenvis_tr_protons.csv')
df_baseline = pd.read_csv('GEANT4_data/build/T_sweep/stormer_pay/P1_T_00_Al_00.csv')
df_passive = pd.read_csv('GEANT4_data/build/T_sweep/stormer_pay/P1_T_00_Al_05.csv')
df_active_1 = pd.read_csv('GEANT4_data/build/T_sweep/stormer_pay/P1_T_20_Al_00.csv')
df_active_2 = pd.read_csv('GEANT4_data/build/T_sweep/stormer_pay/P1_T_20_Al_05_4x.csv')

T_field = 2.0 

initial_energies = df_spenvis['Energy'].values
initial_flux = df_spenvis['Flux'].values

ekin_base = df_baseline['Ekin_MeV'].values
edep_base = df_baseline['Edep_MeV'].values

ekin_pass = df_passive['Ekin_MeV'].values
edep_pass = df_passive['Edep_MeV'].values

ekin_act1 = df_active_1['Ekin_MeV'].values
edep_act1 = df_active_1['Edep_MeV'].values
ekin_act2 = df_active_2['Ekin_MeV'].values
edep_act2 = df_active_2['Edep_MeV'].values

E_min = 1e-3
E_max = 1e3
num_bins = 30
bins_log = np.logspace(np.log10(E_min), np.log10(E_max), num_bins)

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

c_base = '#262626' 
c_pass = '#C42021' 
c_act1 = '#005BBB' 
c_act2 = '#228B22' 

line_w = 2.0 
m_size = 5 

def get_line_data(data, bins):
    counts, bin_edges = np.histogram(data, bins=bins)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    mask = counts > 0
    return bin_centers[mask], counts[mask]

# ==========================================
# PLOT 1: INCIDENT KINETIC ENERGY
# ==========================================
fig1, ax1 = plt.subplots(figsize=(8, 5))

x_base, y_base = get_line_data(ekin_base, bins_log)
x_pass, y_pass = get_line_data(ekin_pass, bins_log)
x_act1, y_act1 = get_line_data(ekin_act1, bins_log)
x_act2, y_act2 = get_line_data(ekin_act2, bins_log)

ax1.plot(x_base, y_base, marker='o', markersize=m_size, linestyle='-', linewidth=line_w, color=c_base, label='Baseline')
ax1.plot(x_pass, y_pass, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive (5 mm Al)')
ax1.plot(x_act1, y_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label=f'Active ({T_field:g} T) no Al')
ax1.plot(x_act2, y_act2/4, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label=f'Active ({T_field:g} T & 5 mm Al)')

ax1.set_xlabel('Kinetic Energy (MeV)', fontsize=12)
ax1.set_ylabel('Number of Hits', fontsize=12)

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim(bottom=0.8) 

ax1.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax1.legend(fontsize=11, loc='upper right')

fig1.tight_layout()
plt.show()

# ==========================================
# PLOT 2: DEPOSITED ENERGY
# ==========================================
fig2, ax2 = plt.subplots(figsize=(8, 5))

x_edep_pass, y_edep_pass = get_line_data(edep_pass, bins_log)
x_edep_act1, y_edep_act1 = get_line_data(edep_act1, bins_log)
x_edep_act2, y_edep_act2 = get_line_data(edep_act2, bins_log)

ax2.plot(x_edep_pass, y_edep_pass, marker='s', markersize=m_size, linestyle='-', linewidth=line_w, color=c_pass, label='Passive (5 mm Al)')
ax2.plot(x_edep_act1, y_edep_act1, marker='^', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act1, label='Active (2 T) no Al')
ax2.plot(x_edep_act2, y_edep_act2/4, marker='x', markersize=m_size, linestyle='-', linewidth=line_w, color=c_act2, label='Active (2 T & 5 mm Al)')

ax2.set_xlabel('Deposited Energy (MeV)', fontsize=12)
ax2.set_ylabel('Number of Hits', fontsize=12)

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_ylim(bottom=0.8)

ax2.grid(True, which="major", ls=":", alpha=0.4, color='gray')
ax2.legend(fontsize=11, loc='upper right')

fig2.tight_layout()
plt.show()