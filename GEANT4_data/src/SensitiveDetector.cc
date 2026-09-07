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
    
    // Recupera l'evento attivo in modo sicuro
    auto eventAction = static_cast<EventAction*>(
        G4EventManager::GetEventManager()->GetUserEventAction()
    );
    
    if (eventAction) {
        // 1. Somma l'Energia Depositata per il calcolo della Dose (solo se > 0)
        if (edep > 0.) {
            eventAction->AddEdep(edep / MeV);
        }

        // 2. Registra l'Energia Cinetica Incidente
        // Vogliamo l'energia SOLO quando la particella entra nel Silicio
        G4StepPoint* preStepPoint = step->GetPreStepPoint();
        if (preStepPoint->GetStepStatus() == fGeomBoundary) {
            G4double ekin = preStepPoint->GetKineticEnergy();
            eventAction->AddEkin(ekin / MeV); // Passiamo l'energia cinetica all'evento
        }
    }

    return true;
}

} // namespace HPM