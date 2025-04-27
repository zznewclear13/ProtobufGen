#pragma once

#include <iostream>
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

public:
    void Print() const
    {
        std::cout << "ClassRoom: " << name << std::endl;
        std::cout << "Students: " << std::endl;
        for (auto& student : students)
        {
            std::cout << "\t" << student.first << ", " << student.second.name << ", " << student.second.age << std::endl;
        }
        std::cout << "Teacher: " << teacher.name << ", " << teacher.age << std::endl;
        std::cout << "Desks: " << std::endl;
        for (auto& desk : desks)
        {
            std::cout << "\t" << desk.name << ", " << desk.material << std::endl;
        }
        std::cout << "Chairs: " << std::endl;
        for (auto& chair : chairs)
        {
            std::cout << "\t" << chair.name << ", " << chair.material << std::endl;
        }
    }
};