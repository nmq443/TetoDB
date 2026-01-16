// Cursor.h

#pragma once

#include "Common.h"

class Table;

class Cursor{
public:
    Cursor(Table* t, int rowNum);
    ~Cursor();

    void AdvanceCursor();
    void* Address();

public:
    Table* table;
    int rowNum;
    bool endOfTable;
};