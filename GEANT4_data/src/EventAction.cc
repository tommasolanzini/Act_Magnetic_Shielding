
/// \file EventAction.cc
/// \brief Implementation of the HPM::EventAction class

#include "EventAction.hh"
#include "G4Event.hh"
#include "G4TrajectoryContainer.hh"
#include "globals.hh"
#include "G4AnalysisManager.hh"

namespace HPM
{

EventAction::EventAction() {}
EventAction::~EventAction() {}

void EventAction::BeginOfEventAction(const G4Event*) {
    // Reset both energy buckets at the start of every particle shower
    fEdep = 0.;
    fEkin = 0.;
}

void EventAction::EndOfEventAction(const G4Event*) {
    // If the particle interacted with the SD (deposited energy or crossed boundary)
    if (fEdep > 0. || fEkin > 0.) {
        auto analysisManager = G4AnalysisManager::Instance();
        
        // Fill Column 0 (Edep) and Column 1 (Ekin)
        analysisManager->FillNtupleDColumn(0, fEdep);
        analysisManager->FillNtupleDColumn(1, fEkin);
        
        analysisManager->AddNtupleRow();
    }
}

}  // namespace HPM