// CommandDispatcher.h

#pragma once

#include "Common.h"

class Database;


void ExecuteCommand(string &line);
Result ProcessCommand(string &line);
void ProcessDotCommand(string &line);