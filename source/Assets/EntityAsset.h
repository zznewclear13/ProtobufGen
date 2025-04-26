#pragma once
#include "Support/ProtoInclude.h"

class EntityAsset
{
public:
    PROTO_PROPERTY_START
    PROTO_STRING name{};
    PROTO_PROPERTY_END
};