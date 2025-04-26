#pragma once

template<typename T>
class Singleton
{
public:
	static T& Get();

	Singleton(const Singleton&) = delete;
	Singleton& operator= (const Singleton) = delete;

protected:
	Singleton() = default;
};

template<typename T>
T& Singleton<T>::Get()
{
	static T instance{ };
	return instance;
}
