
#ifndef eman__cuda_util_h__
#define eman__cuda_util_h__ 1


// Global texture
extern texture<float, 3, cudaReadModeElementType> tex;

// Various utility functions
/** Initialize the cuda device
 * Can be called any number of times but the actual initialization occurs only the first time
 */
void device_init();

/** Get the stored cuda arrary corresponding to the input arguments
 */
int stored_cuda_array(const float* ,const int,const int,const int);

/** Texture binding
 */
void bind_cuda_texture(const int);

#endif // eman__cuda_util_h__