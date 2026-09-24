#ifndef HPMEventAction_h
#define HPMEventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"

class G4Event;

namespace HPM
{

class EventAction : public G4UserEventAction {
  public:
    EventAction();
    ~EventAction() override;

    void BeginOfEventAction(const G4Event* event) override;
    void EndOfEventAction(const G4Event* event) override;

    // Custom methods called by SensitiveDetector
    void RecordParticleEdep(G4double edep, G4int flag);
    void AddEkin(G4double ekin) { if (fEkin == 0.) fEkin = ekin; }

  private:
    G4double fEkin = 0.;
    G4double fTotalEdep = 0.;
    G4double fPrimaryElectronEdep = 0.;
    G4double fPrimaryProtonEdep = 0.;
    G4double fSecondaryEdep = 0.;
};

}  // namespace HPM

#endif