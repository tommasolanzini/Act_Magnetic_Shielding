#include "DetectorConstruction.hh"
#include "SensitiveDetector.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4SDManager.hh"
#include "DipoleMagneticField.hh"
#include "G4UserLimits.hh" // max steps

// Required headers for Magnetic Field physics
#include "G4UniformMagField.hh"
#include "G4FieldManager.hh"
#include "G4TransportationManager.hh"

#include "G4Tubs.hh" // for cylinder

// Constructor
DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(), fLogicAvionics(nullptr)
{}

// Destructor
DetectorConstruction::~DetectorConstruction()
{}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4NistManager* nist = G4NistManager::Instance();
    G4bool checkOverlaps = true;

    // 1. Materials
    G4Material* vacuum = nist->FindOrBuildMaterial("G4_Galactic");
    G4Material* aluminum = nist->FindOrBuildMaterial("G4_Al");
    G4Material* silicon = nist->FindOrBuildMaterial("G4_Si");
    G4Material* pcbMaterial = nist->FindOrBuildMaterial("G4_BAKELITE"); // Proxy for FR4

    // 2. World Volume (Expanded to 100 cm to accommodate larger structures)
    G4double worldSize = 200.0 * cm;
    G4Box* solidWorld = new G4Box("World", worldSize/2, worldSize/2, worldSize/2);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, vacuum, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(nullptr, G4ThreeVector(), logicWorld, "World", nullptr, false, 0, checkOverlaps);

    G4UserLimits* worldLimits = new G4UserLimits();
    worldLimits->SetMaxAllowedStep(1.0 * cm);
    worldLimits->SetUserMaxTrackLength(50.0 * m);
    worldLimits->SetUserMaxTime(10.0 * ms);
    logicWorld->SetUserLimits(worldLimits);

    G4double vaultRadius = 6.1 * cm; 
    G4double vaultHalfLength = 16 * cm; 
    G4Tubs* solidVault = new G4Tubs("Vault", 0.0, vaultRadius, vaultHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicVault = new G4LogicalVolume(solidVault, aluminum, "Vault");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicVault, "Vault", logicWorld, false, 0, checkOverlaps);

    // 4. Inner Vacuum Cavity (6 cm radius, 15 cm half-length)
    G4double cavityRadius = 6.0 * cm;
    G4double cavityHalfLength = 15.0 * cm;
    G4Tubs* solidCavity = new G4Tubs("Cavity", 0.0, cavityRadius, cavityHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicCavity = new G4LogicalVolume(solidCavity, vacuum, "Cavity");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicCavity, "Cavity", logicVault, false, 0, checkOverlaps);
    // 5. Distributed Circular PCBs (Silicon Targets)
    // Radius rigorously calculated to yield exactly 0.228 kg of Silicon across 10 boards
    G4double pcbRadius = 5.581 * cm; 
    G4double pcbHalfThickness = 0.5 * mm; // 1 mm total thickness per board
    
    G4Tubs* solidPCB = new G4Tubs("SolidPCB", 0.0, pcbRadius, pcbHalfThickness, 0.0, 360.0 * deg);
    
    // FIX: Assign this to fLogicAvionics instead of logicPCB
    fLogicAvionics = new G4LogicalVolume(solidPCB, silicon, "LogicPCB");
    
    // Distribute 10 boards evenly along the Z-axis of the 30 cm long cavity
    int numBoards = 10;
    G4double spacing = 2.5 * cm; // Distance between the centers of each board
    
    // Start positioning from the bottom of the cylinder moving upwards
    G4double startZ = -11.25 * cm; 
    
    for (int i = 0; i < numBoards; i++) {
        G4double zPos = startZ + (i * spacing); 
        
        new G4PVPlacement(
            nullptr,                    // No rotation
            G4ThreeVector(0, 0, zPos),  // Position along Z axis
            fLogicAvionics,             // FIX: Use fLogicAvionics here too!
            "PhysicalPCB",              // Name
            logicCavity,                // Mother volume (the vacuum cylinder)
            false,                      // No boolean operations
            i,                          // Copy number (0 to 9)
            checkOverlaps               // Overlap checking
        );
    }

    return physWorld;
}

void DetectorConstruction::ConstructSDandField() {
    // Dipole magnetic shielding
    DipoleMagneticField* magField = new DipoleMagneticField();

    G4FieldManager* globalFieldMgr = G4TransportationManager::GetTransportationManager()->GetFieldManager();
    globalFieldMgr->SetDetectorField(magField);
    globalFieldMgr->CreateChordFinder(magField);

    // ==========================================
    // 2. SENSITIVE DETECTORS
    // ==========================================
    // Attach the Sensitive Detector ONLY to the inner Silicon volume
    auto sdManager = G4SDManager::GetSDMpointer();
    
    // If your SensitiveDetector is in the HPM namespace, we call it like this:
    auto sensitiveDetector = new HPM::SensitiveDetector("AvionicsSD");
    sdManager->AddNewDetector(sensitiveDetector);
    
    // Ensure fLogicAvionics is defined in your DetectorConstruction.hh file
    SetSensitiveDetector(fLogicAvionics, sensitiveDetector);
}