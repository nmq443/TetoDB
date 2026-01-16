// Database.h

#pragma once

#include "Common.h"
class Table;
class Row;

class Database{
public:
    Database(const string& name);
    ~Database();

    Result CreateTable(const string& tableName, stringstream & ss);
    Table* GetTable(const string& name);
    Result DropTable(const string& name);
    Result Insert(const string& name, stringstream& ss);
    vector<Row*> SelectAll(const string& name);

    void LoadFromMeta();
    void FlushToMeta();

public:
    map<string, Table*> tables;
    const string metaFileName;
    bool running;
};