import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture()
def client(monkeypatch, tmp_path):
    test_file = tmp_path / "intern_data.json"
    monkeypatch.setattr(database, "JSON_FILE", str(test_file))
    return TestClient(app)


def add_intern(client, name="Srinivas", role="Python Developer"):
    response = client.post("/interns/AddIntern", json={"name": name, "role": role})
    assert response.status_code == 200
    return response.json()["intern_id"]


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Intern Management API is running"}


def test_add_intern_success(client):
    response = client.post("/interns/AddIntern", json={"name": "Srinivas", "role": "Python Developer"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Intern added successfully"
    assert data["intern_id"] == "INT001"


def test_add_intern_ids_increment_sequentially(client):
    first_id = add_intern(client, "A", "Dev")
    second_id = add_intern(client, "B", "Dev")
    assert first_id == "INT001"
    assert second_id == "INT002"


def test_add_intern_strips_whitespace(client):
    intern_id = add_intern(client, name="   Test Intern   ", role="   Python Developer   ")
    summary = client.get(f"/interns/{intern_id}").json()
    assert summary["name"] == "Test Intern"
    assert summary["role"] == "Python Developer"


def test_add_intern_empty_name_rejected(client):
    response = client.post("/interns/AddIntern", json={"name": "", "role": "Dev"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Name and role cannot be empty"


def test_add_intern_whitespace_only_name_rejected(client):
    response = client.post("/interns/AddIntern", json={"name": "   ", "role": "Dev"})
    assert response.status_code == 400


def test_add_intern_empty_role_rejected(client):
    response = client.post("/interns/AddIntern", json={"name": "Test", "role": ""})
    assert response.status_code == 400


def test_add_intern_missing_role_field(client):
    response = client.post("/interns/AddIntern", json={"name": "Test"})
    assert response.status_code == 422


def test_add_intern_missing_name_field(client):
    response = client.post("/interns/AddIntern", json={"role": "Dev"})
    assert response.status_code == 422


def test_add_intern_non_string_name_rejected_by_schema(client):
    response = client.post("/interns/AddIntern", json={"name": 12345, "role": "Dev"})
    assert response.status_code == 422


def test_add_intern_numeric_looking_string_name_is_allowed(client):
    response = client.post("/interns/AddIntern", json={"name": "12345", "role": "Dev"})
    assert response.status_code == 200


def test_add_intern_new_intern_starts_active_with_no_history(client):
    intern_id = add_intern(client)
    summary = client.get(f"/interns/{intern_id}").json()
    assert summary["status"] == "Active"
    assert summary["total_hours"] == 0
    assert summary["average_hours"] == 0
    assert summary["task_history"] == []
    assert summary["most_recent_activity"] is None


def test_add_activity_success(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 7, "task": "Worked on FastAPI"})
    assert response.status_code == 200
    assert response.json() == {"message": "Activity recorded", "intern_id": intern_id}

    summary = client.get(f"/interns/{intern_id}").json()
    assert summary["total_hours"] == 7
    assert summary["task_history"] == ["Worked on FastAPI"]
    assert summary["most_recent_activity"] == "Worked on FastAPI"


def test_add_activity_accumulates_across_multiple_entries(client):
    intern_id = add_intern(client)
    client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": "Task 1"})
    client.post(f"/interns/{intern_id}/activity", json={"hours": 3, "task": "Task 2"})
    summary = client.get(f"/interns/{intern_id}").json()
    assert summary["total_hours"] == 8
    assert summary["average_hours"] == 4.0
    assert summary["task_history"] == ["Task 1", "Task 2"]
    assert summary["most_recent_activity"] == "Task 2"


def test_add_activity_negative_hours_rejected(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": -5, "task": "x"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Hours must be between 0 and 24"


def test_add_activity_hours_above_24_rejected(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 25, "task": "x"})
    assert response.status_code == 400


def test_add_activity_hours_boundary_values_allowed(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": "0", "task": "x"})
    assert response.status_code == 200
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 24, "task": "y"})
    assert response.status_code == 200


def test_add_activity_non_integer_hours_rejected_by_schema(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": "seven", "task": "x"})
    assert response.status_code == 422


def test_add_activity_fractional_hours_rejected_by_schema(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 7.5, "task": "x"})
    assert response.status_code == 422


def test_add_activity_empty_task_rejected(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Task cannot be empty"


def test_add_activity_whitespace_only_task_rejected(client):
    intern_id = add_intern(client)
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": "   "})
    assert response.status_code == 400


def test_add_activity_for_nonexistent_intern(client):
    response = client.post("/interns/INT999/activity", json={"hours": 5, "task": "x"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Intern not found"


def test_add_activity_blocked_when_inactive(client):
    intern_id = add_intern(client)
    client.patch(f"/interns/{intern_id}/status", json={"status": "Inactive"})
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": "x"})
    assert response.status_code == 400
    assert "Inactive" in response.json()["detail"]


def test_add_activity_blocked_when_completed(client):
    intern_id = add_intern(client)
    client.patch(f"/interns/{intern_id}/status", json={"status": "Completed"})
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": "x"})
    assert response.status_code == 400


def test_add_activity_intern_id_lookup_is_case_insensitive(client):
    intern_id = add_intern(client)  # "INT001"
    response = client.post(f"/interns/{intern_id.lower()}/activity", json={"hours": 3, "task": "lowercase id"})
    assert response.status_code == 200
    summary = client.get(f"/interns/{intern_id}").json()
    assert "lowercase id" in summary["task_history"]


def test_update_status_success(client):
    intern_id = add_intern(client)
    response = client.patch(f"/interns/{intern_id}/status", json={"status": "Inactive"})
    assert response.status_code == 200
    assert response.json() == {"message": "Status updated", "intern_id": intern_id, "status": "Inactive"}


@pytest.mark.parametrize("status", ["Active", "Inactive", "Completed"])
def test_update_status_accepts_all_valid_statuses(client, status):
    intern_id = add_intern(client)
    response = client.patch(f"/interns/{intern_id}/status", json={"status": status})
    assert response.status_code == 200


def test_update_status_invalid_value_rejected(client):
    intern_id = add_intern(client)
    response = client.patch(f"/interns/{intern_id}/status", json={"status": "RandomStatus"})
    assert response.status_code == 400


def test_update_status_is_case_sensitive(client):
    intern_id = add_intern(client)
    response = client.patch(f"/interns/{intern_id}/status", json={"status": "active"})
    assert response.status_code == 400


def test_update_status_for_nonexistent_intern(client):
    response = client.patch("/interns/INT999/status", json={"status": "Inactive"})
    assert response.status_code == 404


def test_update_status_missing_field(client):
    intern_id = add_intern(client)
    response = client.patch(f"/interns/{intern_id}/status", json={})
    assert response.status_code == 422


def test_reactivating_intern_allows_activity_again(client):
    intern_id = add_intern(client)
    client.patch(f"/interns/{intern_id}/status", json={"status": "Inactive"})
    client.patch(f"/interns/{intern_id}/status", json={"status": "Active"})
    response = client.post(f"/interns/{intern_id}/activity", json={"hours": 5, "task": "back at it"})
    assert response.status_code == 200


def test_view_summary_success(client):
    intern_id = add_intern(client)
    client.post(f"/interns/{intern_id}/activity", json={"hours": 7, "task": "Worked on FastAPI"})
    response = client.get(f"/interns/{intern_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["intern_id"] == intern_id
    assert data["total_hours"] == 7
    assert data["average_hours"] == 7.0
    assert data["task_history"] == ["Worked on FastAPI"]


def test_view_summary_average_rounds_to_two_decimals(client):
    intern_id = add_intern(client)
    client.post(f"/interns/{intern_id}/activity", json={"hours": 1, "task": "a"})
    client.post(f"/interns/{intern_id}/activity", json={"hours": 2, "task": "b"})
    client.post(f"/interns/{intern_id}/activity", json={"hours": 2, "task": "c"})
    response = client.get(f"/interns/{intern_id}")
    assert response.json()["average_hours"] == 1.67


def test_view_summary_for_nonexistent_intern(client):
    response = client.get("/interns/INT999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Intern not found"


def test_view_summary_case_insensitive_lookup(client):
    intern_id = add_intern(client)
    response = client.get(f"/interns/{intern_id.lower()}")
    assert response.status_code == 200


def test_statistics_with_no_interns(client):
    response = client.get("/statistics")
    assert response.status_code == 200
    assert response.json() == {
        "total_interns": 0,
        "active_interns": 0,
        "average_hours": 0,
        "top_performer": None,
    }


def test_statistics_when_no_one_has_logged_hours(client):
    add_intern(client, "A", "Dev")
    add_intern(client, "B", "Dev")
    response = client.get("/statistics")
    data = response.json()
    assert data["total_interns"] == 2
    assert data["active_interns"] == 2
    assert data["average_hours"] == 0
    assert data["top_performer"] is None


def test_statistics_counts_and_averages(client):
    id_a = add_intern(client, "A", "Dev")
    id_b = add_intern(client, "B", "Dev")
    client.post(f"/interns/{id_a}/activity", json={"hours": 10, "task": "x"})
    client.post(f"/interns/{id_b}/activity", json={"hours": 4, "task": "y"})
    client.patch(f"/interns/{id_b}/status", json={"status": "Inactive"})

    response = client.get("/statistics")
    data = response.json()
    assert data["total_interns"] == 2
    assert data["active_interns"] == 1
    assert data["average_hours"] == 7.0  # (10 + 4) / 2
    assert data["top_performer"] == {"intern_id": id_a, "name": "A", "total_hours": 10}


def test_statistics_top_performer_breaks_ties_by_first_encountered(client):
    id_a = add_intern(client, "A", "Dev")
    id_b = add_intern(client, "B", "Dev")
    client.post(f"/interns/{id_a}/activity", json={"hours": 5, "task": "x"})
    client.post(f"/interns/{id_b}/activity", json={"hours": 5, "task": "y"})

    response = client.get("/statistics")
    assert response.json()["top_performer"]["intern_id"] == id_a
