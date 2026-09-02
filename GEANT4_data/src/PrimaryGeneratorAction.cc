/// \file PrimaryGeneratorAction.cc
/// \brief Implementation of the HPM::PrimaryGeneratorAction class

#include "PrimaryGeneratorAction.hh"

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "globals.hh"
#include "G4GeneralParticleSource.hh"

namespace HPM
{

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::PrimaryGeneratorAction()
{
  // G4int nofParticles = 1;
  // fParticleGun = new G4ParticleGun(nofParticles);
  fParticleSource = new G4GeneralParticleSource();

  // default particle kinematic

  // G4ParticleDefinition* particleDefinition =
  //   G4ParticleTable::GetParticleTable()->FindParticle("proton");

  // fParticleGun->SetParticleDefinition(particleDefinition);
  // fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.));
  // fParticleGun->SetParticleEnergy(3.0 * GeV);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
  delete fParticleSource;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{
  // This function is called at the begining of event

  // In order to avoid dependence of PrimaryGeneratorAction
  // on DetectorConstruction class we get world volume
  // from G4LogicalVolumeStore.

  // G4double worldZHalfLength = 0;
  // G4LogicalVolume* worldLV = G4LogicalVolumeStore::GetInstance()->GetVolume("World");
  // G4Box* worldBox = nullptr;
  // if (worldLV) worldBox = dynamic_cast<G4Box*>(worldLV->GetSolid());
  // if (worldBox)
  //   worldZHalfLength = worldBox->GetZHalfLength();
  // else {
  //   G4cerr << "World volume of box not found." << G4endl;
  //   G4cerr << "Perhaps you have changed geometry." << G4endl;
  //   G4cerr << "The gun will be place in the center." << G4endl;
  // }

  // // Starting a primary particle close to the world boundary.
  // //
  // fParticleGun->SetParticlePosition(G4ThreeVector(0., 0., -worldZHalfLength + 1 * um));

  fParticleSource->GeneratePrimaryVertex(anEvent);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

}  // namespace HPM
