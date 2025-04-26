#pragma once

#include <type_traits>
#include <memory>
#include <string>
#include <google/protobuf/message.h>

#include "Assets/EntityAsset.h"
#include "ProtoGen/ProtoWrapper.h"
#include "ProtoGen/AllProtoWrappers.h"

// 主模板定义
template <typename DerivedAsset>
class ProtoFactory
{ 
public:
	static DerivedAsset Deserialize(const std::string& data)
	{
		return GetImpl().Deserialize(data);
	}

	static std::string Serialize(const DerivedAsset& asset)
	{
		return GetImpl().Serialize(asset);
	}

	virtual ~ProtoFactory() = default;

private:
	struct ImplBase
	{
		virtual ~ImplBase() = default;
		virtual DerivedAsset Deserialize(const std::string& data) = 0;
		virtual std::string Serialize(const DerivedAsset& asset) = 0;
	};

	template <typename DerivedProto>
    struct Impl : ImplBase
	{
        DerivedAsset Deserialize(const std::string& data) override
		{
            DerivedProto proto;
            proto.ParseFromString(data);
            return ProtoWrapper<DerivedAsset>::FromProto(proto);
        }

		std::string Serialize(const DerivedAsset& asset) override
		{
            DerivedProto proto = ProtoWrapper<DerivedAsset>::ToProto(asset);
            return proto.SerializeAsString();
        }
    }; 

	static ImplBase& GetImpl()
	{
		using BindType = typename ProtoWrapper<DerivedAsset>::BindType;
		static std::unique_ptr<ImplBase> instance = std::make_unique<Impl<BindType>>();
		return *instance;
	}

};