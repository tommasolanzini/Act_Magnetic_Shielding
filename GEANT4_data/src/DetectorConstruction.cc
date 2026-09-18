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

#include "ToroidalMagneticField.hh"


// Constructor
DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction()
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

    G4double vaultRadius = 6.0 * cm; 
    G4double vaultHalfLength = 3.0 * cm; 
    G4Tubs* solidVault = new G4Tubs("Vault", 0.0, vaultRadius, vaultHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicVault = new G4LogicalVolume(solidVault, aluminum, "Vault");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicVault, "Vault", logicWorld, false, 0, checkOverlaps);


    // 4. Inner Vacuum Cavity (6 cm radius, 15 cm half-length)
    G4double cavityRadius = 6.0 * cm;
    G4double cavityHalfLength = 3.0 * cm;
    G4Tubs* solidCavity = new G4Tubs("Cavity", 0.0, cavityRadius, cavityHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicCavity = new G4LogicalVolume(solidCavity, vacuum, "Cavity");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicCavity, "Cavity", logicVault, false, 0, checkOverlaps);

    G4UserLimits* cavityLimits = new G4UserLimits();
    cavityLimits->SetMaxAllowedStep(0.2 * mm); 
    logicCavity->SetUserLimits(cavityLimits);
    // 5. Distributed Annular PCBs (Størmer-Optimized)
    // Total Volume = 98.04 cm^3 -> 0.22834 kg of Silicon
    const G4int numBoards = 10;
    G4double pcbHalfThickness = 0.5 * mm; 
    
    G4double zPos[numBoards] = {-20.05*mm, -15.60*mm, -11.14*mm, -6.68*mm, -2.23*mm, 2.23*mm, 6.68*mm, 11.14*mm, 15.60*mm, 20.05*mm};
    G4double rInner[numBoards] = {14.84*mm, 8.90*mm, 4.90*mm, 2.08*mm, 0.35*mm, 0.35*mm, 2.08*mm, 4.90*mm, 8.90*mm, 14.84*mm};
    G4double rOuter[numBoards] = {49.82*mm, 54.61*mm, 57.61*mm, 59.37*mm, 60.19*mm, 60.19*mm, 59.37*mm, 57.61*mm, 54.61*mm, 49.82*mm};

    for (int i = 0; i < numBoards; i++) {
        G4Tubs* solidPCB = new G4Tubs("SolidPCB", rInner[i], rOuter[i], pcbHalfThickness, 0.0, 360.0 * deg);
        
        G4LogicalVolume* logicPCB = new G4LogicalVolume(solidPCB, silicon, "LogicPCB");
        fLogicPCBs.push_back(logicPCB);
        
        new G4PVPlacement(
            nullptr,                    
            G4ThreeVector(0, 0, zPos[i]), 
            logicPCB,             
            "PhysicalPCB",              
            logicCavity,                
            false,                      
            i,                          
            checkOverlaps               
        );
    }
    return physWorld;
}

void DetectorConstruction::ConstructSDandField() {
    // Dipole magnetic shielding
    DipoleMagneticField* magField = new DipoleMagneticField();
    // ToroidalMagneticField* magField = new ToroidalMagneticField();

    G4FieldManager* globalFieldMgr = G4TransportationManager::GetTransportationManager()->GetFieldManager();
    globalFieldMgr->SetDetectorField(magField);
    globalFieldMgr->CreateChordFinder(magField);

    auto sdManager = G4SDManager::GetSDMpointer();
    auto sensitiveDetector = new HPM::SensitiveDetector("AvionicsSD");
    sdManager->AddNewDetector(sensitiveDetector);
    
    // Attach SD to all 10 PCB rings
    for (auto logicPCB : fLogicPCBs) {
        SetSensitiveDetector(logicPCB, sensitiveDetector);
    }
}