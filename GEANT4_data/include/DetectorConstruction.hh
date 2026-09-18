// Inside DetectorConstruction.hh
#include "G4VUserDetectorConstruction.hh"
#include "G4LogicalVolume.hh"

class DetectorConstruction : public G4VUserDetectorConstruction {
  public:
    DetectorConstruction();
    ~DetectorConstruction() override;

    G4VPhysicalVolume* Construct() override;
    void ConstructSDandField() override;

  private:
    // Remove: std::vector<G4LogicalVolume*> fLogicPCBs;
    // Add this exact line:
    G4LogicalVolume* fLogicAvionics; 
};