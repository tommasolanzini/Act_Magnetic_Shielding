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

# 1. CONSTANTS & PARAMETERS
m_e = 9.1093837015e-31
q, m_p, mu0, MeV_to_J = 1.602176634e-19, 1.67262192369e-27, 4 * np.pi * 1e-7, 1.602176634e-13
E_MeV, B0, r_ref = 30.0, 0.02, 0.97

m_part = m_p

# 2. MAGNETIC RIGIDITY & STORMER LENGTH
p = np.sqrt(2 * m_part * E_MeV * MeV_to_J)
M = B0 * 4 * np.pi * r_ref**3 / mu0
C_St = np.sqrt(mu0 * M / (4 * np.pi * (p / q)))

# 3. 2D SPATIAL GRID
grid_res = 500
rho = np.linspace(1e-5, 0.12, grid_res)
z = np.linspace(-0.12, 0.12, grid_res)
RHO, Z = np.meshgrid(rho, z)

r = np.sqrt(RHO**2 + Z**2)
lam = np.arctan2(Z, RHO)
r_n = r / C_St

# 4. TRANSMISSION PROBABILITY (STØRMER PENUMBRA)
cos_lam = np.clip(np.cos(lam), 1e-10, 1.0)
C_star = (cos_lam / r_n**2) - (2 / (r_n * cos_lam))
P = np.clip((1 - C_star) / 2, 0, 1)

RHO_FULL = np.hstack((-RHO[:, ::-1], RHO))
Z_FULL = np.hstack((Z[:, ::-1], Z))
P_FULL = np.hstack((P[:, ::-1], P))

# 5. ABSOLUTE BOUNDARY (0% LINE)
lam_b = np.linspace(-np.pi / 2, np.pi / 2, 1000)
r_b = (C_St * np.cos(lam_b)**2) / (1 + np.sqrt(1 + np.cos(lam_b)**3))
rho_b, z_b = r_b * np.cos(lam_b), r_b * np.sin(lam_b)

# 6. GEANT4 POLYCONE GENERATION
target_mass_kg = 0.22834
si_density_kg_m3 = 2329.0
target_volume_m3 = target_mass_kg / si_density_kg_m3

sort_idx = np.argsort(z_b)
z_sorted, rho_sorted = z_b[sort_idx], rho_b[sort_idx]
current_volume_m3 = np.abs(np.pi * np.trapz(rho_sorted**2, z_sorted))

scale_factor = (target_volume_m3 / current_volume_m3)**(1/3)
z_scaled, rho_scaled = z_sorted * scale_factor, rho_sorted * scale_factor

num_planes = 24
z_g4 = np.linspace(z_scaled.min(), z_scaled.max(), num_planes)
rho_g4 = np.interp(z_g4, z_scaled, rho_scaled)
rho_g4[0], rho_g4[-1] = 0.0, 0.0  

print("\n" + "="*55)
print("GEANT4 G4Polycone PARAMETERS GENERATED")
print("="*55)
print(f"Target Mass         : {target_mass_kg:.5f} kg")
print(f"Target Volume       : {target_volume_m3*1e6:.2f} cm^3")
print(f"Unscaled Volume     : {current_volume_m3*1e6:.2f} cm^3")
print(f"Geometry Scale Factor: {scale_factor:.5f}\n")

# 7. ANALISI DEL VOLUME VS ENERGIA DI TAGLIO
energies_array = np.linspace(1, 150, 150) # Da 1 MeV a 150 MeV
volumes_cm3 = []

for E in energies_array:
    p_E = np.sqrt(2 * m_part * E * MeV_to_J)
    C_St_E = np.sqrt(mu0 * M / (4 * np.pi * (p_E / q)))
    
    r_b_E = (C_St_E * np.cos(lam_b)**2) / (1 + np.sqrt(1 + np.cos(lam_b)**3))
    rho_b_E, z_b_E = r_b_E * np.cos(lam_b), r_b_E * np.sin(lam_b)
    
    idx_E = np.argsort(z_b_E)
    vol_m3 = np.abs(np.pi * np.trapz((rho_b_E[idx_E])**2, z_b_E[idx_E]))
    volumes_cm3.append(vol_m3 * 1e6) 

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Subplot 1: Trasmissione Penombra
levels = np.linspace(0, 1, 11)
contour = ax1.contourf(RHO_FULL, Z_FULL, P_FULL, levels=levels, cmap='magma', alpha=0.85)
cbar = plt.colorbar(contour, ax=ax1, ticks=levels)
cbar.set_label("Isotropic Transmission Probability", fontsize=11)

ax1.plot(rho_b, z_b, 'w-', linewidth=1.5, label="Absolute Boundary (0%)")
ax1.plot(-rho_b, z_b, 'w-', linewidth=1.5)
ax1.scatter(0, 0, color="white", s=30, zorder=3)
ax1.axhline(0, color="white", linewidth=0.5, alpha=0.5)
ax1.axvline(0, color="white", linewidth=0.5, alpha=0.5)

ax1.set_xlabel(r"$\rho$ [m]", fontsize=12)
ax1.set_ylabel(r"$z$ [m]", fontsize=12)
ax1.set_title(f"Størmer Penumbra\nProtons: E = {E_MeV} MeV, B = {B0} T", fontsize=13)
ax1.axis("equal")
ax1.set_xlim(-0.11, 0.11)
ax1.set_ylim(-0.11, 0.11)
ax1.grid(True, linestyle=":", alpha=0.3, color='white')
ax1.legend(loc='upper right')

# Subplot 2: Volume vs Energy
ax2.plot(energies_array, volumes_cm3, linewidth=2.5, color='#005BBB')
ax2.axvline(E_MeV, color='#C42021', linestyle='--', linewidth=1.5, label=f'Current Target ({E_MeV} MeV)')
ax2.axhline(target_volume_m3*1e6, color='black', linestyle='-.', linewidth=1.5, label=f'Payload Vol ({target_volume_m3*1e6:.1f} cm$^3$)')

ax2.set_xlabel('Proton Cutoff Energy (MeV)', fontsize=12)
ax2.set_ylabel('Absolute Forbidden Region Volume (cm$^3$)', fontsize=12)
ax2.set_title(f'Available Safe Volume vs Shielding Energy (B = {B0} T)', fontsize=13)
ax2.grid(True, which="major", ls=":", alpha=0.5, color='gray')
ax2.legend(fontsize=11)

plt.tight_layout()
plt.show()