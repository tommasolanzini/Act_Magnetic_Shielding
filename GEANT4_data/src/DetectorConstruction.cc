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
    worldLimits->SetUserMaxTrackLength(10.0 * m);
    logicWorld->SetUserLimits(worldLimits);

    // 3. The Radiation Vault (Outer Aluminum Shell)
    G4double vaultSize = 20.0 * cm;
    G4Box* solidVault = new G4Box("Vault", vaultSize/2, vaultSize/2, vaultSize/2);
    G4LogicalVolume* logicVault = new G4LogicalVolume(solidVault, aluminum, "Vault");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicVault, "Vault", logicWorld, false, 0, checkOverlaps);

    // 4. Inner Vacuum Cavity (Creates 10 mm thick Aluminum walls)
    G4double wallThickness = 5.0 * mm;
    G4double cavitySize = vaultSize - (2 * wallThickness);
    G4Box* solidCavity = new G4Box("Cavity", cavitySize/2, cavitySize/2, cavitySize/2);
    G4LogicalVolume* logicCavity = new G4LogicalVolume(solidCavity, vacuum, "Cavity");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicCavity, "Cavity", logicVault, false, 0, checkOverlaps);

    // 5. Realistic Distributed OBC (5 Boards)
    G4double pcbXY = 15.0 * cm;
    G4double pcbZ = 1.6 * mm;
    
    // Silicon distributed over the boards (leaves a 0.5 cm margin around the edges)
    G4double siXY = 14.0 * cm; 
    G4double siZ = 1.0 * mm; 

    G4Box* solidPCB = new G4Box("PCB", pcbXY/2, pcbXY/2, pcbZ/2);
    G4LogicalVolume* logicPCB = new G4LogicalVolume(solidPCB, pcbMaterial, "PCB");
    
    G4Box* solidSi = new G4Box("SiLayer", siXY/2, siXY/2, siZ/2);
    fLogicAvionics = new G4LogicalVolume(solidSi, silicon, "SiLayer"); // The Sensitive Volume

    // Stack 5 boards inside the 18 cm inner cavity
    G4double spacing = 3.0 * cm; 
    G4double startZ = -6.0 * cm; // Stack centered at: -6, -3, 0, +3, +6 cm
    
    for (int i = 0; i < 5; i++) {
        G4double zPosPCB = startZ + (i * spacing);
        G4double zPosSi = zPosPCB + (pcbZ/2) + (siZ/2);

        new G4PVPlacement(nullptr, G4ThreeVector(0, 0, zPosPCB), logicPCB, "PCB_Phys", logicCavity, false, i, checkOverlaps);
        new G4PVPlacement(nullptr, G4ThreeVector(0, 0, zPosSi), fLogicAvionics, "SiLayer_Phys", logicCavity, false, i, checkOverlaps);
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