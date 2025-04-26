#include <iostream>

#include "Core/FileSystem.h"

#include "Assets/Person.h"
#include "ProtoGen/ProtoFactory.h"

#define TOGGLE 2

int main(int argc, char* argv[])
{
    std::cout << "当前工作目录: " << std::filesystem::current_path() << std::endl;

    std::cout << "Protobuff Code Generation Example." << std::endl;
    FileSystem::Get().Init(argc, argv);

#if TOGGLE == 0
    Person person{};
    person.name = "玩家名字七个字";
    person.age = 28;
    std::cout << "Name: " << person.name << ", Age: " << person.age << std::endl;

    std::string fullPath = (FileSystem::Get().GetFullPath("/")).string();
    std::cout << "Full path: " << fullPath << std::endl;

    std::string data = PersonWrapper::SerializeToBinary(person);
    FileSystem::Get().EnsurePath("/");
    PersonWrapper::SerializeToFile(person, "Person.pd");
    std::cout << "Serialized Data: " << data << std::endl;

    Person tempPerson = PersonWrapper::DeserializeFromFile("Person.pd");
    std::cout << "Name: " << tempPerson.name << ", Age: " << tempPerson.age << std::endl;
#elif TOGGLE == 1

    PersonProto pp{};
    pp.set_name("玩家名字七个字");
    pp.set_age(28);
    auto str = pp.SerializeAsString(); 
    std::cout << "Serialized Data: " << str << std::endl;

    auto fullPath = FileSystem::Get().GetFullPath("");
    std::string fullPathStr = fullPath.string();
    std::cout << "Full path: " << fullPathStr << std::endl;
    FileSystem::Get().EnsurePath("");
    FileSystem::Get().Save("Person.pd", str);

    PersonProto tempPP{};
    bool success = tempPP.ParseFromString(str);
    if (!success)
    {
        throw new std::runtime_error("Ewwwwwwwwww");
    }
    std::cout << "Name: " << tempPP.name() << ", Age: " << tempPP.age() << std::endl;

    std::string tempStr = FileSystem::Get().LoadBinary("Person.pd");
    std::string_view strView = std::string_view(tempStr);

    PersonProto tempPPP{};
    bool success2 = tempPPP.ParseFromArray(strView.data(), strView.size());
    if (!success2)
    {
        throw new std::runtime_error("Ewwwwwwwwww");
    }
    std::cout << "Name: " << tempPPP.name() << ", Age: " << tempPPP.age() << std::endl;
#else
    Person person{};
    person.age = 28;
    person.name = "玩家名字七个字";

    auto data = ProtoFactory<Person>::Serialize(person);
    std::cout << "Serialized Data: " << data << std::endl;
    FileSystem::Get().EnsurePath("");
    FileSystem::Get().Save("Person.pd", data);

    Person newPerson = ProtoFactory<Person>::Deserialize(data);
    std::cout << "Name: " << newPerson.name << ", Age: " << newPerson.age << std::endl;

    std::string newData = FileSystem::Get().LoadBinary("Person.pd");
    newPerson = ProtoFactory<Person>::Deserialize(newData);
    std::cout << "Name: " << newPerson.name << ", Age: " << newPerson.age << std::endl;

#endif
    FileSystem::Get().Cleanup();
    system("PAUSE");
    return 0;
}