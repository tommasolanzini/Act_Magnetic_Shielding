#ifndef DipoleMagneticField_h
#define DipoleMagneticField_h 1

#include "G4MagneticField.hh"

class DipoleMagneticField : public G4MagneticField {
public:
    DipoleMagneticField();
    virtual ~DipoleMagneticField();

    // This is the core function Geant4 calls at every microscopic step
    virtual void GetFieldValue(const double Point[4], double* Bfield) const override;
};

#endif