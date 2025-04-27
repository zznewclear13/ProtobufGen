# ProtoGen

ProtoGen是一个使用Protobuf的自定义类序列化和反序列化代码自动生成的示例，它可以根据带有宏标记的头文件生成相应.proto文件，再通过.proto文件生成对应的.pb.cc和.pb.h文件，最终生成.wrapper.h和.wrapper.cpp文件，用于序列化和反序列化一开始的头文件。
感谢DeepSeek老师，DeepSeek老师在整个项目框架和python代码上给了很大的帮助，赛博皮鞭抽了一边又一遍。

## 使用方法

1. 下载并编译Google Protobuf。
```
git clone https://github.com/protocolbuffers/protobuf.git
cd protobuf
git submodule update --init --recursive

mdkir build
cd build
cmake .. -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_BUILD_EXAMPLES=OFF -Dprotobuf_BUILD_SHARED_LIBS=OFF -DCMAKE_CXX_STANDARD=17
cmake --build . --config Release
cmake --install . --prefix "../install/Release" --config Release
cmake --build . --config Debug
cmake --install . --prefix "../install/Debug" --config Debug
```

2. 将编译好的Protobuf库添加到项目中。将protobuf/install/Release/lib和protobuf/install/Debug/lib里的内容放到ProtoGen/library/Release和ProtoGen/library/Debug文件夹中。

3. 双击configure.bat文件，运行配置脚本。

4. 双击build.bat文件，运行构建脚本。

## 流程图

```
+-------------+     GenProto.py     +--------------+
|  Person.h   | ------------------> | Person.proto |
+-------------+                     +--------------+
                                           |
                           +---------------+----------------+
                           |                                |
                      protoc.exe                      GenProtoCpp.py
                           |                                |
                           v                                v
           +-----------------------------+    +-----------------------------+
           |         Person.pb.h         |    |      Person.wrapper.h       |
           +-----------------------------+    +-----------------------------+
           |         Person.pb.cc        |    |      Person.wrapper.cpp     |
           +-----------------------------+    +-----------------------------+
```

## 调用方式

序列化：
```
Person person{};
auto data = ProtoFactory<Person>::Serialize(person);
FileSystem::Get().Save(fileName, data);
```
反序列化：
```
std::string data = FileSystem::Get().LoadBinary(fileName);
Person person = ProtoFactory<Person>::Deserialize(data);
```

## 特色

1. 使用宏标记来标记自定义类需要序列化的属性。
2. 使用模板自动生成proto文件和wrapper类。
3. 自定义类序列化反序列化时，隐藏了proto生成类的调用，减少调用代码的复杂度。

## 待优化的点

目前使用编译时多态，所有头文件都被ProtoFactory.h包含，导致编译时间过长。未来可能会考虑使用运行时多态。