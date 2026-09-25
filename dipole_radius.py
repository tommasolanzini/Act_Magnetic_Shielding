import numpy as np
from scipy import constants as const
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Computer Modern", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.grid": True
})

def plot_heritage_trade_space():
    B_base = 2.0  
    R_base = 0.20 
    
    M_base = (B_base * 4 * np.pi * R_base**3) / const.mu_0
    
    rho_e = 1.68e-8      
    J = 5e6              
    k_power = 100.0      
    
    P_base = (2 * rho_e * J * M_base) / R_base + k_power * 2 * np.pi * R_base
    
    R_1d = np.linspace(0.15, 1.0, 1000)
    B_1d = np.linspace(0.01, 2.5, 1000)
    R_grid, B_grid = np.meshgrid(R_1d, B_1d)
    
    M_grid = (B_grid * 4 * np.pi * R_grid**3) / const.mu_0
    P_grid = (2 * rho_e * J * M_grid) / R_grid + k_power * 2 * np.pi * R_grid
    
    V_ratio_grid = (M_grid / M_base)**1.5

    fig, ax = plt.subplots(figsize=(11, 8))

    contour_p = ax.contourf(R_grid, B_grid, P_grid/1000, levels=30, cmap='Blues', alpha=0.5)
    cbar = fig.colorbar(contour_p, ax=ax)
    cbar.set_label('Total Steady-State Power (kW)', rotation=270, labelpad=15)
    
    ax.contour(R_grid, B_grid, V_ratio_grid, levels=[1.0], colors='green', linewidths=2, linestyles='--')
    ax.contour(R_grid, B_grid, P_grid, levels=[P_base], colors='red', linewidths=2, linestyles='--')
    
    golden_zone = (V_ratio_grid >= 1.0) & (P_grid <= P_base)
    ax.contourf(R_grid, B_grid, golden_zone, levels=[0.5, 1.5], colors=['gold'], alpha=0.2)
    
    
    # 1. Baseline 
    ax.plot(R_base, B_base, marker='o', color='white', markersize=10, markeredgecolor='black', label='Baseline (2.0 T, 20 cm)')
    
    # 2. AMS-02
    ax.plot(0.55, 0.14, marker='^', color='darkred', markersize=11, markeredgecolor='black', label='AMS-02 (0.14 T, 55 cm)')
    ax.text(0.57, 0.14, 'AMS-02', color='darkred', fontsize=12, weight='bold', va='center')
    
    # 3. BESS-Polar
    ax.plot(0.45, 0.80, marker='s', color='darkorange', markersize=10, markeredgecolor='black', label='BESS-Polar (0.8 T, 45 cm)')
    ax.text(0.47, 0.80, 'BESS-Polar', color='darkorange', fontsize=12, weight='bold', va='center')
    
    # 4. Open MRI 
    ax.plot(0.50, 0.50, marker='D', color='indigo', markersize=10, markeredgecolor='black', label='Open MRI (0.5 T, 50 cm)')
    ax.text(0.52, 0.50, 'Open MRI', color='indigo', fontsize=12, weight='bold', va='center')
    
    ax.set_title('Real-World Heritage within the Shielding Trade Space', pad=15, fontsize=15)
    ax.set_xlabel('Coil Radius $R$ (m)', fontsize=13)
    ax.set_ylabel('Peak Magnetic Field $B$ (T)', fontsize=13)

    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color='green', lw=2, linestyle='--', label='Baseline Volume Iso-line'),
        Line2D([0], [0], color='red', lw=2, linestyle='--', label='Baseline Power Iso-line'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='gold', alpha=0.3, markersize=10, label='Golden Zone')
    ]
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + custom_lines, loc='upper right', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_heritage_trade_space()