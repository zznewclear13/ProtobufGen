#pragma once

#include "Support/ProtoInclude.h"
#include PROTO_INCLUDE(Assets/Person.h)

class Teacher : public PROTO_PARENT(Person)
{
public:
    PROTO_PROPERTY_START
    PROTO_INT age{ 0 };
    PROTO_PROPERTY_END
};