#include "FileSystem.h"

void FileSystem::Init(int argc, char* argv[])
{
	if (argc < 2) return;

	resourcePath = argv[1];
}

void FileSystem::Cleanup()
{
}

bool FileSystem::CheckIfExists(std::string_view path)
{
	return std::filesystem::exists(FileSystem::GetFullPath(path));
}

// 通用二进制写入接口（推荐使用string_view）
void FileSystem::Save(std::string_view path, std::string_view data) {
    std::ofstream file(FileSystem::GetFullPath(path), std::ios::binary);
    file.write(data.data(), data.size());
}

std::string FileSystem::LoadBinary(std::string_view path) {
    std::ifstream file(FileSystem::GetFullPath(path), std::ios::binary | std::ios::ate);
    std::string data(file.tellg(), '\0');
    file.seekg(0).read(data.data(), data.size());
    return data;
}

std::stringstream FileSystem::LoadText(std::string_view path)
{
	std::ifstream file(FileSystem::GetFullPath(path));
	if (!file)
	{
		throw; //Todo: better error handling
	}
	std::stringstream buffer;
	buffer << file.rdbuf();
	return buffer;
}