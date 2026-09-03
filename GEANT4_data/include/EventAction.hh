/// \file EventAction.hh
/// \brief Definition of the HPM::EventAction class

#ifndef HPMEventAction_h
#define HPMEventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"

class G4Event;

namespace HPM
{

/// Event action class

class EventAction : public G4UserEventAction {
  public:
    EventAction();
    ~EventAction() override;

    void BeginOfEventAction(const G4Event* event) override;
    void EndOfEventAction(const G4Event* event) override;

    // Function to add energy from the Sensitive Detector
    void AddEdep(G4double edep) { fEdep += edep; }

  private:
    G4double fEdep = 0.;
};
}  // namespace HPM

#endif
