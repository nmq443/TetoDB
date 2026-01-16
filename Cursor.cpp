// Cursor.cpp

#include "Cursor.h"
#include "Schema.h"

Cursor::Cursor(Table* t, int rowNum) 
    : table(t), rowNum(rowNum), endOfTable(rowNum == t->rowCount) {}

Cursor::~Cursor() {}

void* Cursor::Address(){
    return table->RowSlot(rowNum);
}

void Cursor::AdvanceCursor(){
    rowNum++;
    if(rowNum >= table->rowCount) endOfTable = true;
}

