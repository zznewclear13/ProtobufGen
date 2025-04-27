#include <iostream>
#include <unordered_map>

#include "Core/FileSystem.h"
#include "ProtoGen/ProtoFactory.h"

int main(int argc, char* argv[])
{
    std::cout << "当前工作目录: " << std::filesystem::current_path() << std::endl;

    std::cout << "Protobuff Code Generation Example." << std::endl;
    FileSystem::Get().Init(argc, argv);
    FileSystem::Get().EnsurePath("");

    Student student1{};
    student1.name = "张三";
    student1.age = 18;
    Student student2{};
    student2.name = "Alice";
    student2.age = 19;
    Student student3{};
    student3.name = "佐藤";
    student3.age = 20;
    Teacher teacher{};
    teacher.name = "DeepSeek";
    teacher.age = 30;
    Desk desk{};
    desk.name = "desk";
    desk.material = "wood";
    Chair chair1{};
    chair1.name = "chair1";
    chair1.material = "plastic";
    Chair chair2{};
    chair2.name = "chair2";
    chair2.material = "plastic";
    ClassRoom classRoom{};
    classRoom.name = "ClassRoom";

    std::unordered_map<int, Student> students{};
    students[1] = student1;
    students[2] = student2;
    students[3] = student3;
    classRoom.students = students;
    classRoom.teacher = teacher;
    classRoom.desks = std::vector<Desk>{ desk };
    classRoom.chairs = std::vector<Chair>{ chair1, chair2 };

    auto data = ProtoFactory<ClassRoom>::Serialize(classRoom);
    std::stringstream ss;
    ss << std::hex;
    for (auto& c : data)
    {
        ss << std::setw(2) << std::setfill('0') << (int)c;
    }
    std::cout << "Serialized Data: " << ss.str() << std::endl;
    std::string savedFileName = "ClassRoom.pd";
    FileSystem::Get().Save(savedFileName, data);

    ClassRoom classRoomA = ProtoFactory<ClassRoom>::Deserialize(data);
    classRoomA.name = "ClassRoom A";
    classRoomA.Print();

    std::string dataB = FileSystem::Get().LoadBinary(savedFileName);
    ClassRoom classRoomB = ProtoFactory<ClassRoom>::Deserialize(dataB);
    classRoomB.name = "ClassRoom B";
    classRoomB.Print();

    FileSystem::Get().Cleanup();
    system("PAUSE");
    return 0;
}