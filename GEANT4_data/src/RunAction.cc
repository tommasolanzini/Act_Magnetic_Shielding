#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"

namespace HPM {

RunAction::RunAction() {
    auto analysisManager = G4AnalysisManager::Instance();
    analysisManager->SetDefaultFileType("csv");
    
    // CRITICAL FOR MULTI-THREADING: Merge data from all threads into one file
    analysisManager->SetNtupleMerging(true);
    
    analysisManager->CreateNtuple("TID", "Energy Deposition per Event");
    
    // Column 0
    analysisManager->CreateNtupleDColumn("Edep_MeV");
    // Column 1
    analysisManager->CreateNtupleDColumn("Ekin_MeV"); 
    
    analysisManager->FinishNtuple();
}

RunAction::~RunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    auto analysisManager = G4AnalysisManager::Instance();
    analysisManager->OpenFile("simulation_baseline.csv");
}

void RunAction::EndOfRunAction(const G4Run*) {
    auto analysisManager = G4AnalysisManager::Instance();
    analysisManager->Write();
    analysisManager->CloseFile();
}

} // namespace HPM