#ifndef FRAMagneticField_HH
#define FRAMagneticField_HH

#include "G4MagneticField.hh"
#include <vector>

struct FRALoop {
    double radius;
    double z;
    double current;
};

class FRAMagneticField : public G4MagneticField {
public:
    FRAMagneticField();
    virtual ~FRAMagneticField();

    virtual void GetFieldValue(const double Point[4], double* Bfield) const override;

private:
    std::vector<FRALoop> coils;
    void SetupCoils(double r_in, double r_out, int n_loops, double i_out);
};

#endif