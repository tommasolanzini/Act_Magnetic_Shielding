import numpy as np
import pandas as pd
from tudatpy import constants
from tudatpy.interface import spice
from tudatpy.astro import element_conversion
from tudatpy.numerical_simulation import environment_setup, propagation_setup, environment
from tudatpy import numerical_simulation
from tudatpy.astro import time_representation
import matplotlib.pyplot as plt

# 1. Load Standard SPICE Kernels
spice.load_standard_kernels()

# 2. Environment Setup
bodies_to_create = ["Jupiter", "Sun", "Io", "Europa", "Ganymede", "Callisto"]
global_frame_origin = "Jupiter"
global_frame_orientation = "ECLIPJ2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Add the Spacecraft
bodies.create_empty_body("Spacecraft")
bodies.get("Spacecraft").mass = 1000.0

# 3. Acceleration Setup
# Point mass gravity from Jupiter, the Sun, and major moons
accelerations_settings_spacecraft = dict(
    Jupiter=[propagation_setup.acceleration.point_mass_gravity()],
    Sun=[propagation_setup.acceleration.point_mass_gravity()],
    Io=[propagation_setup.acceleration.point_mass_gravity()],
    Europa=[propagation_setup.acceleration.point_mass_gravity()]
)
acceleration_settings = {"Spacecraft": accelerations_settings_spacecraft}
bodies_to_propagate = ["Spacecraft"]
central_bodies = ["Jupiter"]

acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies)

# 4. Initial State Setup (Highly Elliptical Orbit)
# Jupiter's radius is ~71,492 km. We set periapsis near 2 R_J (deep in radiation belts)
# and apoapsis at 15 R_J.
# 4. Initial State Setup (Circular Orbit at Europa)
r_jup = 71492e3
initial_keplerian_elements = np.array([
    9.5 * r_jup,             # Semi-major axis (a) locked at 9.5 R_J
    0.0,                     # Eccentricity (e) set to 0.0 for a perfect circle
    np.deg2rad(10.0),        # Inclination (i)
    np.deg2rad(0.0),         # Argument of periapsis (omega)
    np.deg2rad(0.0),         # Right ascension of ascending node (RAAN)
    np.deg2rad(0.0)          # True anomaly (theta)
])

# initial_keplerian_elements = np.array([
#     8.5 * r_jup,             # Semi-major axis (a)
#     0.76,                    # Eccentricity (e)
#     np.deg2rad(10.0),        # Inclination (i)
#     np.deg2rad(0.0),         # Argument of periapsis (omega)
#     np.deg2rad(0.0),         # Right ascension of ascending node (RAAN)
#     np.deg2rad(0.0)          # True anomaly (theta)
# ])


mu_jupiter = bodies.get("Jupiter").gravitational_parameter
initial_state = element_conversion.keplerian_to_cartesian(
    initial_keplerian_elements, mu_jupiter)

# 5. Integrator Settings 
fixed_step_size = 3600.0 
integrator_settings = propagation_setup.integrator.runge_kutta_4(fixed_step_size)

# 6. Propagation Settings
simulation_start_epoch = time_representation.iso_string_to_epoch("2030-01-01T00:00:00")
simulation_end_epoch = simulation_start_epoch + 30.0 * constants.JULIAN_DAY # 30 giorni

termination_condition = propagation_setup.propagator.time_termination(simulation_end_epoch)

propagator_settings = propagation_setup.propagator.translational(
    central_bodies,
    acceleration_models,
    bodies_to_propagate,
    initial_state,
    simulation_start_epoch,
    integrator_settings,
    termination_condition
)

# 7. Run Simulation (API 1.0+)
dynamics_simulator = numerical_simulation.create_dynamics_simulator(
    bodies, propagator_settings
)

states = dynamics_simulator.state_history
time_list = []
x_list, y_list, z_list = [], [], []

J2000_JD = 2451545.0

for epoch, state in states.items():
    # Julian Date standard (JDCT)
    jd_time = J2000_JD + (epoch / constants.JULIAN_DAY)
    time_list.append(jd_time)
    
    x_list.append(state[0] / 1000.0) 
    y_list.append(state[1] / 1000.0)
    z_list.append(state[2] / 1000.0)

df = pd.DataFrame({'JDCT': time_list, 'X': x_list, 'Y': y_list, 'Z': z_list})
header = """Title = Jupiter Capture Orbit
Planet = Jupiter
Coordinates = PEI
Columns = JDCT, X, Y, Z
Format = CSV
$$BEGIN
"""

with open("SPENVIS_data/spenvis_trajectory2.txt", "w") as f:
    f.write(header)
    df.to_csv(f, sep=',', index=False, header=False)
    f.write("$$END\n")

print("Trajectory formattata correttamente in CSV per SPENVIS!")

plt.figure(figsize=(10, 8))
plt.plot(x_list, y_list, label='Spacecraft Trajectory', color='blue')
plt.title('Spacecraft Trajectory around Jupiter')
plt.xlabel('X Position (km)')
plt.ylabel('Y Position (km)')
plt.grid()
# Plot Jupiter's position   
plt.scatter(0, 0, color='orange', s=500, label='Jupiter')
plt.legend()
plt.axis('equal')
plt.show()