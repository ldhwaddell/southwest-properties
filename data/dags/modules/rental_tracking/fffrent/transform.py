def get_building_name(building: str) -> str:
    """Simple lookup table with the buildings owned by paramount who lists on 444rent"""
    building = building.lower()
    if "5450 kaye" in building:
        return "St Joseph's Square"
    if "5 horizon" in building:
        return "Avonhurst Gardens"
    elif "1530 birmingham" in building:
        return "Vertu Suites"
    elif "5144 morris" in building:
        return "Vic Suites"
    elif "1239 barrington" in building:
        return "W Suites"
    elif "1078 tower" in building:
        return "Tower Apartments"
    elif "31 russell lake" in building:
        return "Lakecrest Estates"
    elif "5251 south" in building:
        return "Hillside Suites"
    elif "19 irishtown" in building:
        return "Losts at Greenvale"
    elif "1343 hollis" in building:
        return "Waterford Suites"
    elif "1363 hollis" in building:
        return "Flynn Flats"
    elif "6016 pepperell" in building:
        return "The George"
    elif "7037 mumford" in building:
        return "West22 Living"
    elif "1254 hollis" in building:
        return "Acadia Suites"
    elif "5157 morris" in building:
        return "Renaissance South"
    else:
        return building
    
    
    
                #     # Create an id using the building name and unit:
                # id_str = (
                #     row_data["building"] + row_data["unit"]
                #     if row_data["unit"]
                #     else row_data["building"]
                # )
                # row_data["id"] = generate_hash(id_str)