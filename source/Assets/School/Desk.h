#pragma once

#include <string>

#include "Support/ProtoInclude.h"
#include PROTO_INCLUDE(Assets/EntityAsset.h)

class Desk : public PROTO_PARENT(EntityAsset)
{
public:
    PROTO_PROPERTY_START
    PROTO_STRING material{};
    PROTO_PROPERTY_END
};