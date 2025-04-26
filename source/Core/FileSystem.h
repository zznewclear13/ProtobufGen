#pragma once
#include <filesystem>
#include <fstream>
#include <string_view>

#include "Support/Singleton.h"

class FileSystem : public Singleton<FileSystem>
{
	friend class Singleton<FileSystem>;
public:
	void Init(int argc, char* argv[]);
	void Cleanup();
    bool CheckIfExists(std::string_view path);
    void EnsurePath(std::string_view path) { std::filesystem::create_directories(GetFullPath(path)); }
    const std::filesystem::path& GetResourcePath() const { return resourcePath; }
    inline std::filesystem::path GetFullPath(std::string_view path) const { return resourcePath / path; }

    void Save(std::string_view path, std::string_view data);
    std::string LoadBinary(std::string_view path);
    std::stringstream LoadText(std::string_view path);
    
private:
	std::filesystem::path resourcePath{ "Resources" };
};