find_package(OpenGL REQUIRED)

message_var(OPENGL_INCLUDE_DIR)
message_var(OPENGL_LIBRARIES)

if(OpenGL_FOUND AND NOT TARGET OpenGL)
	add_library(OpenGL INTERFACE)
	add_library(OpenGL::OpenGL ALIAS OpenGL)
	set_target_properties(OpenGL PROPERTIES
						  INTERFACE_COMPILE_DEFINITIONS USE_OPENGL
						  )
	target_link_libraries(OpenGL INTERFACE OpenGL::GL OpenGL::GLU)
		
endif()
