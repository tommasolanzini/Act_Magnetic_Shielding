/// \file RunAction.hh
/// \brief Definition of the HPM::RunAction class

#ifndef HPMRunAction_h
#define HPMRunAction_h 1

#include "G4UserRunAction.hh"
#include "globals.hh"

class G4Run;

namespace HPM
{

/// Run action class

class RunAction : public G4UserRunAction
{
  public:
    RunAction();
    ~RunAction() override;

    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;
};

}  // namespace HPM

#endif
