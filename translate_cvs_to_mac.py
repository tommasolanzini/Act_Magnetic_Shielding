import pandas as pd

def generate_gps_macro(input_csv, output_mac, particle_type="e-"):
    """
    Reads a SPENVIS spectrum CSV and generates a GEANT4 GPS macro.
    """
    # 1. Load the data
    # SPENVIS files usually have a large header. Adjust 'skiprows' to match your file.
    df = pd.read_csv(input_csv, skiprows=0)
    
    # Update these exact strings to match the column headers in your CSV
    energy_col = 'Energy' 
    flux_col = 'Flux'

    # 2. Write the Macro
    with open(output_mac, 'w') as f:
        # Define Particle Type and Isotropic Source Geometry
        f.write(f"/gps/particle {particle_type}\n")
        f.write("/gps/pos/type Surface\n")
        f.write("/gps/pos/shape Sphere\n")
        # Sphere radius set to 15 cm to fully encompass your 10x10x10 cm 1U avionics
        f.write("/gps/pos/radius 15. cm\n") 
        f.write("/gps/ang/type cos\n\n")

        # Define Energy Distribution as Arbitrary
        f.write("/gps/ene/type Arb\n")
        f.write("/gps/hist/type arb\n")

        # Write Data Points (Energy vs. Flux)
        for index, row in df.iterrows():
            energy = row[energy_col]
            flux = row[flux_col]
            
            # GEANT4 hates zero-flux points for log interpolation, so we skip them
            if flux > 0:
                f.write(f"/gps/hist/point {energy} {flux}\n")
        
        # Logarithmic interpolation is most accurate for space radiation spectra
        f.write("\n/gps/ene/inter Log\n") 

    print(f"Success! Macro generated at: {output_mac}")

generate_gps_macro("SPENVIS_data/spenvis_tr_electrons.csv", "GEANT4_data/electrons.mac", particle_type="e-")
generate_gps_macro("SPENVIS_data/spenvis_tr_protons.csv", "GEANT4_data/protons.mac", particle_type="proton")