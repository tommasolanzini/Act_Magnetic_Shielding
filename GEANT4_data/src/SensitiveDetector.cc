#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "EventAction.hh"
#include "G4EventManager.hh" 
#include "G4StepPoint.hh"
#include "G4VProcess.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include <fstream>
#include <mutex>

// Static mutex to prevent multi-threading crashes when writing to the file
static std::mutex csvMutex;

namespace HPM {

SensitiveDetector::SensitiveDetector(const G4String& name)
  : G4VSensitiveDetector(name)
{}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4Track* track = step->GetTrack();

    // 1. Only track primary particles (ignores secondary radiation created inside the silicon)
    if (track->GetTrackID() != 1) return false;

    // 2. Only record the exact moment the proton crosses the boundary INTO the silicon
    // This prevents recording thousands of micro-steps as the proton travels inside the block
    if (step->GetPreStepPoint()->GetStepStatus() == fGeomBoundary) {
        
        G4ThreeVector hitPos = step->GetPreStepPoint()->GetPosition();
        G4ThreeVector startPos = track->GetVertexPosition();

        // 3. Thread-safe file writing
        std::lock_guard<std::mutex> lock(csvMutex);
        
        // Opens the file in append mode. 
        // NOTE: You must manually delete "HitCoordinates.csv" before starting a fresh run!
        std::ofstream file("HitCoordinates.csv", std::ios::app);
        
        // Output format: HitX, HitY, HitZ, StartX, StartY, StartZ (in mm)
        file << hitPos.x() << "," << hitPos.y() << "," << hitPos.z() << ","
             << startPos.x() << "," << startPos.y() << "," << startPos.z() << "\n";
             
        file.close();
    }

    return true;
}

} // namespace HPM