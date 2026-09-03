//
// ********************************************************************
// * License and Disclaimer                                           *
// ... (standard Geant4 header comments) ...
// ********************************************************************
//
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
    // Reset the energy bucket at the start of every particle shower
    fEdep = 0.;
}

void EventAction::EndOfEventAction(const G4Event*) {
    // If energy was deposited, write it to the CSV file
    if (fEdep > 0.) {
        auto analysisManager = G4AnalysisManager::Instance();
        analysisManager->FillNtupleDColumn(0, fEdep);
        analysisManager->AddNtupleRow();
    }
}

}  // namespace HPM