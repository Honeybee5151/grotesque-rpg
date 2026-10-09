@echo off
if not defined GODOT (
  echo GODOT is not set. Start the team with team\Start-Team.ps1 1>&2
  exit /b 1
)
"%GODOT%" %*
