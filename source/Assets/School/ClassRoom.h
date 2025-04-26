#pragma once

#include <string>
#include <unordered_map>

#include "Support/ProtoInclude.h"
#include PROTO_INCLUDE(Assets/EntityAsset.h)
#include PROTO_INCLUDE(Assets/School/Student.h)
#include PROTO_INCLUDE(Assets/School/Teacher.h)
#include PROTO_INCLUDE(Assets/School/Desk.h)
#include PROTO_INCLUDE(Assets/School/Chair.h)

class ClassRoom : public PROTO_PARENT(EntityAsset)
{
public:
    PROTO_PROPERTY_START
    PROTO_MAP(PROTO_INT, Student) students;
    PROTO_TYPE(Teacher) teacher;
    PROTO_VECTOR(Desk) desks;
    PROTO_VECTOR(Chair) chairs;
    PROTO_PROPERTY_END
};