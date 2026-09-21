#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "EventAction.hh"
#include "G4EventManager.hh" 
#include "G4StepPoint.hh"
#include "G4VProcess.hh"

namespace HPM {

SensitiveDetector::SensitiveDetector(const G4String& name)
  : G4VSensitiveDetector(name)
{}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4double edep = step->GetTotalEnergyDeposit();
    
    auto eventAction = static_cast<EventAction*>(
        G4EventManager::GetEventManager()->GetUserEventAction()
    );
    
    if (eventAction) {
        if (edep > 0.) {
            eventAction->AddEdep(edep / MeV);
        }
        G4StepPoint* preStepPoint = step->GetPreStepPoint();
        if (preStepPoint->GetStepStatus() == fGeomBoundary) {
            G4double ekin = preStepPoint->GetKineticEnergy();
            eventAction->AddEkin(ekin / MeV); 
        }
    }

    return true;
}

} // namespace HPM