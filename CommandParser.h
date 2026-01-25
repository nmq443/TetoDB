//CommandParser.h

#pragma once
#include "Common.h"

struct ParsedCommand {
    string type; // CREATE, INSERT, SELECT, DROP
    string tableName;
    vector<string> args;
    bool isValid;
    string errorMessage;
};

class CommandParser {
public:
    static ParsedCommand Parse(const string& line);
};