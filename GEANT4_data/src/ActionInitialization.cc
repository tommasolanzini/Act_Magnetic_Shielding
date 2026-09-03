#include "ActionInitialization.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"

namespace HPM {

// Constructor and Destructor are removed here because they are already in your .hh file

void ActionInitialization::BuildForMaster() const {
    // Master thread handles the final CSV file
    SetUserAction(new RunAction());
}

void ActionInitialization::Build() const {
    // Worker threads handle the physics and events
    SetUserAction(new PrimaryGeneratorAction());
    SetUserAction(new RunAction());
    SetUserAction(new EventAction());
}

} // namespace HPM