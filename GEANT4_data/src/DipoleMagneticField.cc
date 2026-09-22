#include "DipoleMagneticField.hh"
#include "G4SystemOfUnits.hh"
#include <cmath>

DipoleMagneticField::DipoleMagneticField() {}

DipoleMagneticField::~DipoleMagneticField() {}

void DipoleMagneticField::GetFieldValue(const double Point[4], double* Bfield) const {
    double x = Point[0];
    double y = Point[1];
    double z = Point[2];
    double r = std::sqrt(x*x + y*y + z*z);

    // 1. The Field-Free Interior (Updated to the 7 cm Aluminum Vault)
    if (r < 0.1 * cm) {
        Bfield[0] = 0.0;
        Bfield[1] = 0.0;
        Bfield[2] = 0.0;
        return;
    }

    // 2. The Dipole Exterior (Aligned to Z-axis)
    // Calibrated to peak exactly at the 7 cm hull boundary
    G4double peakB = 1.5 * tesla; // Adjust this for your 1T, 2T, etc. tests
    double k = peakB * std::pow(20.0 * cm, 3); 
    double r5 = std::pow(r, 5);

    // Dipole equations aligned along the Z-axis (matching the G4Tubs)
    Bfield[0] = (3.0 * x * z * k) / r5;
    Bfield[1] = (3.0 * y * z * k) / r5;
    Bfield[2] = ((3.0 * z * z - r*r) * k) / r5;
}