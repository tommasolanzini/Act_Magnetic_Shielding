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

    // 1. The Field-Free Interior (Inside the Aluminum Vault)
    if (r < 15.0 * cm) {
        Bfield[0] = 0.0;
        Bfield[1] = 0.0;
        Bfield[2] = 0.0;
        return;
    }

    // 2. The Dipole Exterior
    // We calibrate the magnetic moment 'k' so that B = 1.0 Tesla exactly at r = 15 cm
    double k = 1.0 * tesla * std::pow(15.0 * cm, 3);
    double r5 = std::pow(r, 5);

    // Dipole equations aligned along the Y-axis
    Bfield[0] = (3.0 * x * y * k) / r5;
    Bfield[1] = ((3.0 * y * y - r*r) * k) / r5;
    Bfield[2] = (3.0 * z * y * k) / r5;
}