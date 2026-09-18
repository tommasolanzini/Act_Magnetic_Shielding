#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"
#include <vector>


class G4VPhysicalVolume;
class G4LogicalVolume;

class DetectorConstruction : public G4VUserDetectorConstruction
{
  public:

    DetectorConstruction();
    ~DetectorConstruction() override;

    G4VPhysicalVolume* Construct() override;
    
    // Add this exact line to declare the Sensitive Detector construction
    void ConstructSDandField() override;


  private:
    std::vector<G4LogicalVolume*> fLogicPCBs; // I volumi di silicio per calcolare la dose
};

#endif