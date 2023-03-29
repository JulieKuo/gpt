# Get activate area list from grid_config.json
def get_area_list(channel_name, area_dict):
    active_area_list = None
    if channel_name in area_dict.keys():
        area_info_dict = area_dict[channel_name]
        active_area_list = [area for area in area_info_dict.keys() if area_info_dict[area]["activate"]]
    return active_area_list


# Remove non-activate area from logic
def area_filter(param, area_list):
    area_key = "area"  # mode 0 = "target", mode 1,2,3 = "area"
    if param["sop_mode"] == 0.0:
        area_key = "target"
    temp_param_list = []
    for area_dict in param[area_key]:
        if area_dict["name"] in area_list:
            temp_param_list.append(area_dict)
    param[area_key] = temp_param_list

    return param
