#pragma once

#include <string>
#include <vector>
#include <unordered_map>

#define PROTO_INCLUDE(x) #x
#define PROTO_PARENT(x) x

#define PROTO_PROPERTY_START
#define PROTO_PROPERTY_END

#define PROTO_FLOAT float
#define PROTO_INT int32_t
#define PROTO_SIZE_T size_t
#define PROTO_STRING std::string
#define PROTO_VECTOR(x) std::vector<x>
#define PROTO_MAP(k, v) std::unordered_map<k, v>
#define PROTO_TYPE(x) x