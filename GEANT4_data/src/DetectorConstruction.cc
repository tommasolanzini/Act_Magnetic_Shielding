#include "DetectorConstruction.hh"

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4NistManager.hh"
#include "G4SystemOfUnits.hh"

DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(), fScoringVolume(nullptr)
{}

DetectorConstruction::~DetectorConstruction()
{}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
    G4NistManager* nist = G4NistManager::Instance();

    // 1. Materiali
    G4Material* galactic = nist->FindOrBuildMaterial("G4_Galactic"); // Vuoto spaziale
    G4Material* silicon  = nist->FindOrBuildMaterial("G4_Si");       // Silicio avionica

    // 2. World Volume (Scatola di 1 m x 1 m x 1 m)
    G4double world_size = 1.0 * m;
    G4Box* solidWorld = new G4Box("World", 0.5*world_size, 0.5*world_size, 0.5*world_size);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, galactic, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(
        0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true
    );

    // 3. Avionics Volume: Cubo 1U (10 cm x 10 cm x 10 cm)
    G4double u1_size = 10.0 * cm;
    G4Box* solidAvionics = new G4Box("Avionics1U", 0.5*u1_size, 0.5*u1_size, 0.5*u1_size);
    G4LogicalVolume* logicAvionics = new G4LogicalVolume(solidAvionics, silicon, "Avionics1U");
    
    // Piazzamento del cubo al centro del mondo
    new G4PVPlacement(
        0, G4ThreeVector(), logicAvionics, "Avionics1U", logicWorld, false, 0, true
    );

    fScoringVolume = logicAvionics;

    return physWorld;
}