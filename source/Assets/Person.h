#pragma once

#include <string>
#include <vector>

#include "Support/ProtoInclude.h"
#include PROTO_INCLUDE(Assets/EntityAsset.h)

class Person : public PROTO_PARENT(EntityAsset)
{
public:
	PROTO_PROPERTY_START
	PROTO_STRING name{};
	PROTO_INT age{0};
	PROTO_PROPERTY_END
};