import numpy as np
import matplotlib.pyplot as plt

# 1. CONSTANTS & PARAMETERS
q, m_p, mu0, MeV_to_J = 1.602176634e-19, 1.67262192369e-27, 4 * np.pi * 1e-7, 1.602176634e-13
E_MeV, B0, r_ref = 5.0, 1.0, 0.20

# 2. MAGNETIC RIGIDITY & STORMER LENGTH
p = np.sqrt(2 * m_p * E_MeV * MeV_to_J)
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

# Mirror grid for plotting
RHO_FULL = np.hstack((-RHO[:, ::-1], RHO))
Z_FULL = np.hstack((Z[:, ::-1], Z))
P_FULL = np.hstack((P[:, ::-1], P))

# 5. ABSOLUTE BOUNDARY (0% LINE)
lam_b = np.linspace(-np.pi / 2, np.pi / 2, 1000)
r_b = (C_St * np.cos(lam_b)**2) / (1 + np.sqrt(1 + np.cos(lam_b)**3))
rho_b, z_b = r_b * np.cos(lam_b), r_b * np.sin(lam_b)

# 6. GEANT4 POLYCONE GENERATION
# Target metrics for Silicon
target_mass_kg = 0.22834
si_density_kg_m3 = 2329.0
target_volume_m3 = target_mass_kg / si_density_kg_m3

# Sort coordinates to ensure Z is monotonically increasing for G4Polycone
sort_idx = np.argsort(z_b)
z_sorted, rho_sorted = z_b[sort_idx], rho_b[sort_idx]

# Calculate current volume using the trapezoidal rule: V = pi * integral(rho^2 dz)
current_volume_m3 = np.abs(np.pi * np.trapz(rho_sorted**2, z_sorted))

# Scale coordinates to perfectly match target volume (Volume scales with r^3)
scale_factor = (target_volume_m3 / current_volume_m3)**(1/3)
z_scaled, rho_scaled = z_sorted * scale_factor, rho_sorted * scale_factor

# Downsample to a reasonable number of planes for the Geant4 navigator
num_planes = 24
z_g4 = np.linspace(z_scaled.min(), z_scaled.max(), num_planes)
rho_g4 = np.interp(z_g4, z_scaled, rho_scaled)
rho_g4[0], rho_g4[-1] = 0.0, 0.0  # Force close the tips of the "apple"

print("\n" + "="*55)
print("GEANT4 G4Polycone PARAMETERS GENERATED")
print("="*55)
print(f"Target Mass         : {target_mass_kg:.5f} kg")
print(f"Target Volume       : {target_volume_m3*1e6:.2f} cm^3")
print(f"Unscaled Volume     : {current_volume_m3*1e6:.2f} cm^3")
print(f"Geometry Scale Factor: {scale_factor:.5f}\n")

# Print C++ Arrays
print(f"const G4int numZPlanes = {num_planes};")
print("G4double zPlane[] = {\n    " + ", ".join([f"{val*1000:.3f}*mm" for val in z_g4]) + "\n};")
print("G4double rInner[] = {\n    " + ", ".join(["0.0*mm"] * num_planes) + "\n};")
print("G4double rOuter[] = {\n    " + ", ".join([f"{val*1000:.3f}*mm" for val in rho_g4]) + "\n};\n")
print("="*55 + "\n")

# 7. PLOT
plt.figure(figsize=(10, 8))
levels = np.linspace(0, 1, 11)
contour = plt.contourf(RHO_FULL, Z_FULL, P_FULL, levels=levels, cmap='magma', alpha=0.85)
cbar = plt.colorbar(contour, ticks=levels)
cbar.set_label("Isotropic Transmission Probability", fontsize=11)

plt.plot(rho_b, z_b, 'w-', linewidth=1.5, label="Absolute Boundary (0%)")
plt.plot(-rho_b, z_b, 'w-', linewidth=1.5)
plt.scatter(0, 0, color="white", s=30, zorder=3)
plt.axhline(0, color="white", linewidth=0.5, alpha=0.5)
plt.axvline(0, color="white", linewidth=0.5, alpha=0.5)

plt.xlabel(r"$\rho$ [m]")
plt.ylabel(r"$z$ [m]")
plt.title(f"Størmer Penumbra Transmission Field\nProtons: E = {E_MeV} MeV, B = {B0} T")
plt.axis("equal")
plt.xlim(-0.11, 0.11)
plt.ylim(-0.11, 0.11)
plt.grid(True, linestyle=":", alpha=0.3, color='white')
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()