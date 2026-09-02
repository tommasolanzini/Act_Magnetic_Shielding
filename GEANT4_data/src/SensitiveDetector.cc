#ifndef SensitiveDetector_h
#define SensitiveDetector_h 1

#include "G4VSensitiveDetector.hh"

namespace HPM {

class SensitiveDetector : public G4VSensitiveDetector {
  public:
    SensitiveDetector(const G4String& name);
    ~SensitiveDetector() override = default;

    // This function triggers every time a particle takes a step inside your volume
    G4bool ProcessHits(G4Step* step, G4TouchableHistory* history) override;
};

} // namespace HPM
#endif