import os
import numpy as np
import matplotlib.pyplot as plt

# 1. Geant4 Payload Geometry Arrays (in mm)
zPlane = np.array([-14.854, -14.839, -13.357, -11.874, -10.392, -8.909, -7.427, -5.945, -4.462, -2.980, -1.497, -0.015, 0.015, 1.497, 2.980, 4.462, 5.945, 7.427, 8.909, 10.392, 11.874, 13.357, 14.839, 14.854])
rInner = np.array([0.000, 14.480, 10.537, 7.952, 5.998, 4.429, 3.144, 2.078, 1.229, 0.569, 0.121, 0.000, 0.000, 0.121, 0.569, 1.229, 2.078, 3.144, 4.429, 5.998, 7.952, 10.537, 14.480, 0.000])
rOuter = np.array([0.000, 24.380, 27.987, 30.213, 31.804, 33.018, 33.967, 34.677, 35.176, 35.515, 35.692, 35.719, 35.719, 35.692, 35.515, 35.176, 34.677, 33.967, 33.018, 31.804, 30.213, 27.987, 24.380, 0.000])

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 2. Generate the 3D surface of the Polycone
theta = np.linspace(0, 2 * np.pi, 50)
THETA, Z = np.meshgrid(theta, zPlane)

# Outer surface ("Apple")
R_OUT = np.tile(rOuter, (len(theta), 1)).T
X_OUT = R_OUT * np.cos(THETA)
Y_OUT = R_OUT * np.sin(THETA)

# Inner surface ("Hourglass" hole)
R_IN = np.tile(rInner, (len(theta), 1)).T
X_IN = R_IN * np.cos(THETA)
Y_IN = R_IN * np.sin(THETA)

# Plot payload surfaces with high transparency
ax.plot_surface(X_OUT, Y_OUT, Z, alpha=0.15, color='cyan', edgecolor='none')
ax.plot_surface(X_IN, Y_IN, Z, alpha=0.3, color='blue', edgecolor='none')

# 3. Load and plot hit data
file_path = "GEANT4_data/build/HitCoordinates.csv"
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    data = np.loadtxt(file_path, delimiter=",")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    
    hit_x, hit_y, hit_z = data[:, 0], data[:, 1], data[:, 2]
    ax.scatter(hit_x, hit_y, hit_z, c='red', s=15, label=f'Proton Impacts ({len(hit_x)})', zorder=5)
else:
    print("No hits found or file does not exist. The shield is perfectly reflecting!")
    ax.plot([], [], ' ', label="0 Proton Impacts")

# 4. Formatting
ax.set_xlabel('X [mm]')
ax.set_ylabel('Y [mm]')
ax.set_zlabel('Z [mm]')
ax.set_title('Payload Impact Map with Størmer Geometry')

# Lock the aspect ratio so the cylinder doesn't look stretched
ax.set_xlim([-40, 40])
ax.set_ylim([-40, 40])
ax.set_zlim([-20, 20])
ax.set_box_aspect([1, 1, 0.5]) 
ax.legend()
plt.show()