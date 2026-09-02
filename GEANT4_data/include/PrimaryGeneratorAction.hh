// / \file PrimaryGeneratorAction.hh
// / \brief Definition of the HPM::PrimaryGeneratorAction class

#ifndef HPMPrimaryGeneratorAction_h
#define HPMPrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"

class G4GeneralParticleSource;
class G4Event;

namespace HPM
{

/// The primary generator action class with General Particle Source (GPS).
/// It allows driving the simulation using external macro files (.mac).

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
  public:
    PrimaryGeneratorAction();
    ~PrimaryGeneratorAction() override;

    void GeneratePrimaries(G4Event*) override;

    G4GeneralParticleSource* GetParticleSource() { return fParticleSource; }

  private:
    G4GeneralParticleSource* fParticleSource = nullptr;  // G4 general particle source
};

}  // namespace HPM

#endif
