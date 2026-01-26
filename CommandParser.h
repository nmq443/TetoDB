//CommandParser.h

#pragma once

#include <string>
#include <vector>

using namespace std;

struct ParsedCommand {
    string type; // CREATE, INSERT, SELECT, DROP, DELETE
    string tableName;
    vector<string> args;
    bool isValid;
    string errorMessage;
};

class CommandParser {
public:
    static ParsedCommand Parse(const string& line);
};