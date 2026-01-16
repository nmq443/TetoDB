// CommandDispatcher.h

#pragma once

#include "Common.h"

class Database;

Result ProcessCommand(string &line);
void ProcessDotCommand(string &line);