CHECK_REQUIRED_LIB(FFTW3F fftw3f fftw3.h libfftw3f-3 "")
CHECK_REQUIRED_LIB(FFTW3D fftw3 fftw3.h libfftw3-3  "")
CHECK_REQUIRED_LIB(FFTW3F_THREADS fftw3f_threads fftw3.h "" "")
CHECK_REQUIRED_LIB(FFTW3D_THREADS fftw3_threads fftw3.h ""  "")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(FFTW3
		REQUIRED_VARS
			FFTW3F_INCLUDE_PATH
			FFTW3F_LIBRARY
			FFTW3D_INCLUDE_PATH
			FFTW3D_LIBRARY
			FFTW3F_THREADS_INCLUDE_PATH
			FFTW3F_THREADS_LIBRARY
			FFTW3D_THREADS_INCLUDE_PATH
			FFTW3D_THREADS_LIBRARY
		)

if(FFTW3_FOUND 
   AND NOT TARGET FFTW3 
   AND NOT TARGET FFTW3F 
   AND NOT TARGET FFTW3D
   AND NOT TARGET FFTW3F_THREADS 
   AND NOT TARGET FFTW3D_THREADS
   )
	foreach(trgt FFTW3F FFTW3D FFTW3 FFTW3F_THREADS FFTW3D_THREADS)
		add_library(${trgt} INTERFACE)
		add_library(${trgt}::${trgt} ALIAS ${trgt})
	endforeach()
	foreach(trgt FFTW3F FFTW3D FFTW3F_THREADS FFTW3D_THREADS)
		set_target_properties(${trgt} PROPERTIES
							  INTERFACE_INCLUDE_DIRECTORIES "${${trgt}_INCLUDE_PATH}"
							  INTERFACE_LINK_LIBRARIES      "${${trgt}_LIBRARY}"
							  )
	endforeach()
		
	set_target_properties(FFTW3 PROPERTIES
						  INTERFACE_COMPILE_DEFINITIONS USE_FFTW3
						  )
	target_link_libraries(FFTW3 INTERFACE FFTW3F::FFTW3F FFTW3D::FFTW3D FFTW3F_THREADS::FFTW3F_THREADS FFTW3D_THREADS::FFTW3D_THREADS)
endif()
