#include <stdio.h>
#include <stdlib.h>

FILE* open_file(char* file_name, char* prevs){
	FILE *out=fopen(file_name,prevs);
	return out;
}

__declspec(dllexport) char* xorData(const unsigned char* data, size_t arrays_cnt, const size_t values_cnt){
	printf(*data);
	unsigned char* result = (unsigned char*)malloc(values_cnt*arrays_cnt);
	for (size_t i = 0; i < arrays_cnt; i++)
	{
		result[i] = *(data+i);
		for (size_t j = 1; j < values_cnt; j++)
		{
			result[i] ^= (unsigned char)(data[arrays_cnt*j+i]);
		}
		
	}
	return result;

}

