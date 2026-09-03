#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "EventAction.hh"
#include "G4EventManager.hh" // Swapped from G4RunManager to G4EventManager

namespace HPM {

SensitiveDetector::SensitiveDetector(const G4String& name)
  : G4VSensitiveDetector(name)
{}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4double edep = step->GetTotalEnergyDeposit();
    
    // Ignore empty hits
    if (edep == 0.) return false;

    // Grab the active event safely using the Event Manager
    auto eventAction = static_cast<EventAction*>(
        G4EventManager::GetEventManager()->GetUserEventAction()
    );
    
    if (eventAction) {
        eventAction->AddEdep(edep / MeV);
    }

    return true;
}

} // namespace HPM