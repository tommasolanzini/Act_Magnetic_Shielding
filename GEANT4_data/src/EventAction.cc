#include "EventAction.hh"
#include "G4Event.hh"
#include "G4AnalysisManager.hh"

namespace HPM
{

EventAction::EventAction() {}
EventAction::~EventAction() {}

void EventAction::BeginOfEventAction(const G4Event*) {
    // CRITICAL: Reset ALL buckets at the start of every particle shower
    fEkin = 0.;
    fTotalEdep = 0.;
    fPrimaryElectronEdep = 0.;
    fPrimaryProtonEdep = 0.;
    fSecondaryEdep = 0.;
}

void EventAction::RecordParticleEdep(G4double edep, G4int flag) {
    if (flag == 1) {
        fPrimaryElectronEdep += edep;
    } else if (flag == 2) {
        fPrimaryProtonEdep += edep;
    } else if (flag == 3 || flag == 4) {
        // Grouping Gammas (3) and Secondary Electrons (4) together. 
        // Gammas often eject secondary electrons in the silicon to deposit energy!
        fSecondaryEdep += edep;
    }
    
    // Always keep track of the total
    fTotalEdep += edep; 
}

void EventAction::EndOfEventAction(const G4Event*) {
    // Only write to CSV if energy was actually deposited in the silicon
    if (fTotalEdep > 0.) {
        auto analysisManager = G4AnalysisManager::Instance();
        analysisManager->FillNtupleDColumn(0, fEkin);
        analysisManager->FillNtupleDColumn(1, fTotalEdep);
        analysisManager->FillNtupleDColumn(2, fPrimaryElectronEdep);
        analysisManager->FillNtupleDColumn(3, fPrimaryProtonEdep);
        analysisManager->FillNtupleDColumn(4, fSecondaryEdep);
        analysisManager->AddNtupleRow();
    }
}

}  // namespace HPM