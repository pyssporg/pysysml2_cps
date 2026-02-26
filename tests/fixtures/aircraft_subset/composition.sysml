package Aircraft {
  part def AircraftBaseComposition {
    doc /* Reusable base composition with common subsystem structure. */
    attribute profile = "base";
    attribute obsolete = true;

    part autopilot : AutopilotModule;
    part missionComputer : MissionComputer;
    part environment : Environment;

    connect autopilot.autopilotCmd to missionComputer.autopilotInput;
    connect missionComputer.direction_command to environment.direction_command;
    connect environment.orientation to autopilot.currentOrientation;
    connect environment.location to autopilot.currentLocation;
    connect environment.flight_status to autopilot.feedbackBus;
  }

  part def AircraftComposition : AircraftBaseComposition {
    doc /* Top-level aircraft composition with functional subsystem instances. */

    remove attribute obsolete;
    replace attribute profile = "operational";
    attribute variant = "f16";

    replace part missionComputer : MissionComputer;

    remove connect missionComputer.direction_command to environment.direction_command;
    connect missionComputer.direction_command to environment.direction_command;
  }
}
