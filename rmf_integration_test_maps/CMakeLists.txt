cmake_minimum_required(VERSION 3.5)

project(rmf_integration_test_maps)

find_package(ament_cmake REQUIRED)

#install(DIRECTORY
#  maps/
#  DESTINATION share/${PROJECT_NAME}
#)

ament_package()

#file(GLOB_RECURSE traffic_editor_paths "maps/*.building.yaml")

# ros2 run rmf_test_map_tools matrix_generator -r 8 -c 8 -n 2 -o OUTPUT_PATH

set(world_name "matrix882")
set(map_path ${CMAKE_CURRENT_BINARY_DIR}/maps/${world_name}.building.yaml)
set(output_world_name ${world_name})
set(output_dir ${CMAKE_CURRENT_BINARY_DIR}/maps/${output_world_name})
set(output_world_path ${output_dir}/${output_world_name}.world)
set(output_model_dir ${output_dir}/models)

add_custom_command(
  COMMAND ros2 run rmf_test_map_tools matrix_generator -r 8 -c 8 -n 2 -o ${map_path}
  OUTPUT ${map_path}
)

install(FILES
  ${map_path}
  DESTINATION share/${PROJECT_NAME}/maps
)

add_custom_command(
  COMMAND ros2 run rmf_building_map_tools building_map_generator gazebo ${map_path} ${output_world_path} ${output_model_dir}
  OUTPUT ${output_world_path}
  DEPENDS ${map_path}
)

set(ign_output_dir ${CMAKE_CURRENT_BINARY_DIR}/maps/${output_world_name}_ign)
set(ign_output_world_path ${ign_output_dir}/${output_world_name}.world)
set(ign_output_model_dir ${ign_output_dir}/models)

add_custom_command(
  OUTPUT ${ign_output_world_path}
  COMMAND ros2 run rmf_building_map_tools building_map_generator ignition ${map_path} ${ign_output_world_path} ${ign_output_model_dir}
  DEPENDS ${map_path}
)

add_custom_target(generate_${world_name} ALL
  DEPENDS ${output_world_path} ${ign_output_world_path}
)

install(
  DIRECTORY ${ign_output_dir}
  DESTINATION share/${PROJECT_NAME}/maps
)

install(
  DIRECTORY ${output_dir}
  DESTINATION share/${PROJECT_NAME}/maps
)

set(output_nav_graphs_dir ${output_dir}/nav_graphs/)
set(output_nav_graphs_phony ${output_nav_graphs_dir}/phony)
add_custom_command(
  OUTPUT ${output_nav_graphs_phony}
  COMMAND ros2 run rmf_building_map_tools building_map_generator nav ${map_path} ${output_nav_graphs_dir}
  DEPENDS ${map_path}
)

add_custom_target(generate_${output_world_name}_nav_graphs ALL
  DEPENDS ${output_nav_graphs_phony}
)
