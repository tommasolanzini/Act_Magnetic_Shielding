#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "EventAction.hh"
#include "G4EventManager.hh" 
#include "G4StepPoint.hh"
#include "G4VProcess.hh"
#include "G4Track.hh"
#include "G4ParticleDefinition.hh"

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
        // --- 1. IDENTIFY PARTICLE TYPE ---
        G4Track* track = step->GetTrack();
        G4String particleName = track->GetDefinition()->GetParticleName();
        G4int parentID = track->GetParentID(); 
        
        G4int particleFlag = 0; // Default
        
        if (parentID == 0 && particleName == "e-") {
            particleFlag = 1; // Primary Electron
        } 
        else if (parentID == 0 && particleName == "proton") {
            particleFlag = 2; // Primary Proton
        } 
        else if (parentID > 0 && particleName == "gamma") {
            particleFlag = 3; // Secondary Photon (Bremsstrahlung)
        } 
        else if (parentID > 0 && particleName == "e-") {
            particleFlag = 4; // Secondary Electron (Delta ray / Compton)
        }

        // --- 2. RECORD ENERGY DEPOSITION ---
        if (edep > 0.) {
            // Send the energy and the specific particle flag to EventAction
            eventAction->RecordParticleEdep(edep / MeV, particleFlag);
        }

        // --- 3. RECORD INCIDENT KINETIC ENERGY ---
        G4StepPoint* preStepPoint = step->GetPreStepPoint();
        if (preStepPoint->GetStepStatus() == fGeomBoundary) {
            G4double ekin = preStepPoint->GetKineticEnergy();
            eventAction->AddEkin(ekin / MeV);
        }
    }

    return true;
}

} // namespace HPM