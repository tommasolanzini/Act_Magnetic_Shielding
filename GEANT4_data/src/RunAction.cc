#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"

namespace HPM {

RunAction::RunAction() {
    auto analysisManager = G4AnalysisManager::Instance();
    analysisManager->SetDefaultFileType("csv");
    analysisManager->SetNtupleMerging(true);
    
    analysisManager->CreateNtuple("Hits", "Edep Data by Particle");
    analysisManager->CreateNtupleDColumn("Ekin_MeV");         // Column 0
    analysisManager->CreateNtupleDColumn("Total_Edep_MeV");   // Column 1
    analysisManager->CreateNtupleDColumn("Electron_Edep_MeV");// Column 2
    analysisManager->CreateNtupleDColumn("Proton_Edep_MeV");  // Column 3
    analysisManager->CreateNtupleDColumn("Gamma_Edep_MeV");   // Column 4
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