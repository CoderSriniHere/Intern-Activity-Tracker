from database import read_data

"""The actual function of the statistics is here, 
The endpoints are in the router folder"""

async def overall_statistics():
    data = await read_data()

    if not data:
        return {
            "total_interns": 0,
            "active_interns": 0,
            "average_hours": 0,
            "top_performer": None,
        }

    total_interns = len(data)
    active_interns = len([i for i in data if i["status"] == "Active"])

    all_hours = []
    for intern in data:
        all_hours.extend(intern["hours"])
    overall_average = (sum(all_hours) / len(all_hours)) if all_hours else 0

    top_performer = max(data, key=lambda i: sum(i["hours"]))
    top_total_hours = sum(top_performer["hours"])

    return {
        "total_interns": total_interns,
        "active_interns": active_interns,
        "average_hours": round(overall_average, 2),
        "top_performer": {
            "intern_id": top_performer["intern_id"],
            "name": top_performer["name"],
            "total_hours": top_total_hours,
        } if top_total_hours > 0 else None,
    }
