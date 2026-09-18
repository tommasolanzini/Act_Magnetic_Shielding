#include "DetectorConstruction.hh"
#include "SensitiveDetector.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4SDManager.hh"
#include "DipoleMagneticField.hh"
#include "G4UserLimits.hh"
#include "G4UniformMagField.hh"
#include "G4FieldManager.hh"
#include "G4TransportationManager.hh"
#include "G4Tubs.hh" 
#include "G4Polycone.hh" // Required for the monolithic Størmer shape

DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(), fLogicAvionics(nullptr)
{}

DetectorConstruction::~DetectorConstruction()
{}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4NistManager* nist = G4NistManager::Instance();
    G4bool checkOverlaps = true;

    G4Material* vacuum = nist->FindOrBuildMaterial("G4_Galactic");
    G4Material* aluminum = nist->FindOrBuildMaterial("G4_Al");
    G4Material* silicon = nist->FindOrBuildMaterial("G4_Si");

    // 1. World Volume
    G4double worldSize = 200.0 * cm;
    G4Box* solidWorld = new G4Box("World", worldSize/2, worldSize/2, worldSize/2);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, vacuum, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(nullptr, G4ThreeVector(), logicWorld, "World", nullptr, false, 0, checkOverlaps);

    G4UserLimits* worldLimits = new G4UserLimits();
    worldLimits->SetMaxAllowedStep(1.0 * cm);
    worldLimits->SetUserMaxTrackLength(50.0 * m);
    worldLimits->SetUserMaxTime(10.0 * ms);
    logicWorld->SetUserLimits(worldLimits);

    // 2. Vault
    G4double vaultRadius = 6.0 * cm; 
    G4double vaultHalfLength = 3.0 * cm; 
    G4Tubs* solidVault = new G4Tubs("Vault", 0.0, vaultRadius, vaultHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicVault = new G4LogicalVolume(solidVault, aluminum, "Vault");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicVault, "Vault", logicWorld, false, 0, checkOverlaps);

    // 3. Inner Vacuum Cavity
    G4double cavityRadius = 6.0 * cm;
    G4double cavityHalfLength = 3.0 * cm;
    G4Tubs* solidCavity = new G4Tubs("Cavity", 0.0, cavityRadius, cavityHalfLength, 0.0, 360.0 * deg);
    G4LogicalVolume* logicCavity = new G4LogicalVolume(solidCavity, vacuum, "Cavity");
    new G4PVPlacement(nullptr, G4ThreeVector(), logicCavity, "Cavity", logicVault, false, 0, checkOverlaps);

    // 4. Strict Limits for Magnetic Tracking
    G4UserLimits* cavityLimits = new G4UserLimits();
    cavityLimits->SetMaxAllowedStep(0.2 * mm); 
    logicCavity->SetUserLimits(cavityLimits);
    
    // 5. Monolithic Størmer Payload (Hourglass Hole + Apple Exterior)
    // Volume rigorously scaled to exactly 98.04 cm^3 (0.22834 kg of Silicon)
    const G4int numZPlanes = 24;
    G4double zPlane[] = {
        -14.854*mm, -14.839*mm, -13.357*mm, -11.874*mm, -10.392*mm, -8.909*mm, -7.427*mm, -5.945*mm, -4.462*mm, -2.980*mm, -1.497*mm, -0.015*mm, 0.015*mm, 1.497*mm, 2.980*mm, 4.462*mm, 5.945*mm, 7.427*mm, 8.909*mm, 10.392*mm, 11.874*mm, 13.357*mm, 14.839*mm, 14.854*mm
    };
    G4double rInner[] = {
        14.480*mm, 14.480*mm, 10.537*mm, 7.952*mm, 5.998*mm, 4.429*mm, 3.144*mm, 2.078*mm, 1.229*mm, 0.569*mm, 0.121*mm, 0.000*mm, 0.000*mm, 0.121*mm, 0.569*mm, 1.229*mm, 2.078*mm, 3.144*mm, 4.429*mm, 5.998*mm, 7.952*mm, 10.537*mm, 14.480*mm, 14.480*mm
    };
    G4double rOuter[] = {
        24.380*mm, 24.380*mm, 27.987*mm, 30.213*mm, 31.804*mm, 33.018*mm, 33.967*mm, 34.677*mm, 35.176*mm, 35.515*mm, 35.692*mm, 35.719*mm, 35.719*mm, 35.692*mm, 35.515*mm, 35.176*mm, 34.677*mm, 33.967*mm, 33.018*mm, 31.804*mm, 30.213*mm, 27.987*mm, 24.380*mm, 24.380*mm
    };

    G4Polycone* solidAvionics = new G4Polycone(
        "SolidAvionics", 0.0*deg, 360.0*deg, numZPlanes, zPlane, rInner, rOuter
    );
    
    fLogicAvionics = new G4LogicalVolume(solidAvionics, silicon, "LogicAvionics");
    
    new G4PVPlacement(
        nullptr, G4ThreeVector(0, 0, 0), fLogicAvionics, "PhysicalAvionics", logicCavity, false, 0, checkOverlaps               
    );

    return physWorld;
}

void DetectorConstruction::ConstructSDandField() {
    DipoleMagneticField* magField = new DipoleMagneticField();

    G4FieldManager* globalFieldMgr = G4TransportationManager::GetTransportationManager()->GetFieldManager();
    globalFieldMgr->SetDetectorField(magField);
    globalFieldMgr->CreateChordFinder(magField);

    auto sdManager = G4SDManager::GetSDMpointer();
    auto sensitiveDetector = new HPM::SensitiveDetector("AvionicsSD");
    sdManager->AddNewDetector(sensitiveDetector);
    
    SetSensitiveDetector(fLogicAvionics, sensitiveDetector);
}