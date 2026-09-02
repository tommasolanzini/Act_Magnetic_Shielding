import pandas as pd
import matplotlib.pyplot as plt

def generate_gps_macro_and_plot(input_csv, output_mac, plot_filename, particle_type="e-", num_particles=1000):
    """
    Reads a SPENVIS spectrum CSV, generates a GEANT4 GPS macro, and saves a log-log plot.
    """
    df = pd.read_csv(input_csv, skiprows=0)
    
    energy_col = 'Energy' 
    flux_col = 'Flux'

    # --- 1. Generate the GEANT4 Macro ---
    with open(output_mac, 'w') as f:
        f.write("/run/initialize\n\n")
        f.write(f"/gps/particle {particle_type}\n")
        f.write("/gps/pos/type Surface\n")
        f.write("/gps/pos/shape Sphere\n")
        f.write("/gps/pos/radius 15. cm\n") 
        f.write("/gps/ang/type cos\n\n")

        f.write("/gps/ene/type Arb\n")
        f.write("/gps/hist/type arb\n")

        for index, row in df.iterrows():
            energy = row[energy_col]
            flux = row[flux_col]
            if flux > 0:
                f.write(f"/gps/hist/point {energy} {flux}\n")
        
        f.write("\n/gps/hist/inter Log\n") 
        f.write(f"\n/run/beamOn {num_particles}\n")

    print(f"Macro generated at: {output_mac}")

    # --- 2. Generate the Plot for Overleaf ---
    plt.figure(figsize=(8, 6))
    
    # Choose color based on particle
    color = '#1f77b4' if particle_type == 'e-' else '#d62728'
    label_name = 'Electrons' if particle_type == 'e-' else 'Protons'
    
    plt.plot(df[energy_col], df[flux_col], marker='o', markersize=4, linestyle='-', color=color, label=label_name)
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Energy (MeV)', fontsize=12)
    plt.ylabel(r'Flux (cm$^{-2}$ s$^{-1}$ sr$^{-1}$ MeV$^{-1}$)', fontsize=12)
    plt.title(f'Jovian Trapped {label_name} Spectrum', fontsize=14)
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    
    # Save as PDF for lossless Overleaf integration
    plt.show()
    # plt.savefig(plot_filename, format='pdf', bbox_inches='tight')
    plt.close()
    
    
    print(f"Plot saved to: {plot_filename}\n")

# Run the function for both particles
generate_gps_macro_and_plot("SPENVIS_data/spenvis_tr_electrons.csv", 
                            "GEANT4_data/macros/electrons.mac", 
                            "electrons_spectrum.pdf", 
                            particle_type="e-")

generate_gps_macro_and_plot("SPENVIS_data/spenvis_tr_protons.csv", 
                            "GEANT4_data/macros/protons.mac", 
                            "protons_spectrum.pdf", 
                            particle_type="proton")